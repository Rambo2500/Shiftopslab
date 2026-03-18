from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from workforce_engine.database import get_db
from workforce_engine.schemas.employee import (
    EmployeeCreate, EmployeeResponse, 
    EmployeeAvailabilityCreate, EmployeeAvailabilityResponse
)
from workforce_engine.services.employee_service import create_employee
from workforce_engine.models import Employee, EmployeeAvailability, AvailabilityStatus, DepartmentType, EmploymentStatus

from typing import Optional, List
from datetime import date
import pandas as pd
from io import BytesIO

from workforce_engine.services.roster_service import RosterService

router = APIRouter(prefix="/employees", tags=["Employees"])


def parse_file_to_dict_list(file: UploadFile) -> List[dict]:
    """Helper to convert uploaded CSV/Excel to list of dicts with basic cleaning."""
    filename = file.filename.lower()
    content = file.file.read()
    
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(content), sep=None, engine='python')
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload CSV or Excel.")

        # Normalize Column Names
        df.columns = [str(c).strip() for c in df.columns]
        mapping = {
            "Employee ID": "employee_id",
            "Name": "full_name",
            "EmpName_1": "full_name",  # TempWorks
            "deptname": "department",   # TempWorks
            "Team": "team",
            "Role": "role_type",
            "Schedulable": "is_schedulable",
            "jobtitle": "jobtitle"
        }

        # Rename columns if they exist in the mapping
        rename_map = {k: v for k, v in mapping.items() if k in df.columns}
        df.rename(columns=rename_map, inplace=True)

        # Handle Name Split if "full_name" exists
        if "full_name" in df.columns:
            df = df.dropna(subset=['full_name'])
            split_names = df['full_name'].astype(str).str.split(',', expand=True, n=1)
            df['last_name'] = split_names[0].str.strip()
            if split_names.shape[1] > 1:
                df['first_name'] = split_names[1].str.strip()
            else:
                df['first_name'] = ""

        # Ensure defaults for missing required fields to prevent total failure
        if 'first_name' not in df.columns: df['first_name'] = ""
        if 'last_name' not in df.columns: df['last_name'] = ""

        # Replace NaN with None
        df = df.where(pd.notnull(df), None)

        # Basic validation: ensure we have names at the very least
        required = ["first_name", "last_name"]
        missing = [c for c in required if c not in df.columns]
        if missing:
             # Fallback check for TempWorks specific columns
             tw_columns = ["jobtitle", "EmpName_1", "OrderID"]
             if not any(c in df.columns for c in tw_columns):
                  raise HTTPException(status_code=400, detail=f"Missing identifying columns: {missing}")

        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

@router.post("/availability", response_model=EmployeeAvailabilityResponse)
def report_absence(
    availability: EmployeeAvailabilityCreate,
    db: Session = Depends(get_db)
):
    # Upsert availability
    existing = db.query(EmployeeAvailability).filter(
        EmployeeAvailability.employee_id == availability.employee_id,
        EmployeeAvailability.date == availability.target_date
    ).first()

    if existing:
        existing.status = availability.status
        existing.reason = availability.reason
    else:
        existing = EmployeeAvailability(
            employee_id=availability.employee_id,
            date=availability.target_date,
            status=availability.status,
            reason=availability.reason
        )
        db.add(existing)
    
    db.commit()
    db.refresh(existing)
    return existing


@router.get("/availability/{employee_id}", response_model=List[EmployeeAvailabilityResponse])
def get_employee_availability(
    employee_id: str,
    db: Session = Depends(get_db)
):
    return db.query(EmployeeAvailability).filter(EmployeeAvailability.employee_id == employee_id).all()


@router.post("/roster/ingest")
async def ingest_workforce_data(
    site_id: str,
    department: Optional[str] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Unified ingestion endpoint.
    Detects if it's a Roster or TempWorks file and processes accordingly.
    """
    data = parse_file_to_dict_list(file)
    if not data:
        raise HTTPException(status_code=400, detail="File is empty or could not be parsed.")

    # Detection Logic: TempWorks files usually have 'EmpName_1' or 'jobtitle'
    sample = data[0]
    is_tempworks = "jobtitle" in sample or "EmpName_1" in sample or "OrderID" in sample

    try:
        if is_tempworks:
            # For TempWorks, we use the reconcile logic
            result = RosterService.reconcile_tempworks(db, site_id, data)
            result["type_detected"] = "TempWorks Assignment Export"
        else:
            # For Roster, we use the initial upload logic
            if department:
                for row in data:
                    if not row.get('department'):
                        row['department'] = department
            result = RosterService.upload_initial_roster(db, site_id, data)
            result["type_detected"] = "Standard Roster"

        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/roster/upload")
async def upload_roster(
    site_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    roster_data = parse_file_to_dict_list(file)
    return RosterService.upload_initial_roster(db, site_id, roster_data)


@router.post("/roster/reconcile")
async def reconcile_roster(
    site_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    tw_data = parse_file_to_dict_list(file)
    return RosterService.reconcile_tempworks(db, site_id, tw_data)


@router.post("/add-new-hires")
async def add_new_hires(
    site_id: str,
    payload: List[dict],
    db: Session = Depends(get_db)
):
    """
    Directly converts detected new hires (from TempWorks) into Roster employees.
    payload: [{"name": "MULLINS, TARA", "team": "P1"}, ...]
    """
    created_count = 0
    
    for row in payload:
        raw_name = row.get("name", "")
        team = row.get("team", "").upper()
        if not raw_name or not team:
            continue
            
        # Parse Name
        if "," in raw_name:
            parts = raw_name.split(",", 1)
            last = parts[0].strip()
            first = parts[1].strip()
        else:
            parts = raw_name.split(None, 1)
            first = parts[0].strip()
            last = parts[1].strip() if len(parts) > 1 else "Unknown"

        # Check for existing
        existing = db.query(Employee).filter(
            Employee.first_name == first,
            Employee.last_name == last,
            Employee.site_id == site_id
        ).first()
        
        if existing:
            # Just update team if they already exist
            existing.team = team
            existing.active = True
            continue

        # Determine Department from Team
        dept = DepartmentType.PACKING
        if team in ["A", "B", "C", "D", "AB"]:
            dept = DepartmentType.SHIPPING

        # Create
        emp = Employee(
            site_id=site_id,
            first_name=first,
            last_name=last,
            team=team,
            department=dept,
            active=True,
            employment_status=EmploymentStatus.ACTIVE,
            is_schedulable=True,
            is_rotating=(dept == DepartmentType.PACKING) # Packing rotates by default
        )
        db.add(emp)
        created_count += 1
        
    db.commit()
    return {"created": created_count}


@router.post("/", response_model=EmployeeResponse)
def create_employee_endpoint(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_employee(db, employee)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[EmployeeResponse])
def list_employees(
    active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Employee)
    if active is not None:
        query = query.filter(Employee.active == active)
    return query.all()
