from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from workforce_engine.models import Employee, DepartmentType, ShiftType, EmploymentStatus, RoleType
from datetime import datetime
import logging
import pandas as pd

logger = logging.getLogger("workforce_engine.roster_service")

class RosterService:

    MANAGEMENT_NAMES = ["ASHE, JAMES", "THOMSON, JAMES"] 

    @staticmethod
    def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        The 'Bulletproof' Normalizer. 
        Translates any messy input row into a clean internal dictionary.
        """
        # 1. Helper for truthy values (Schedulable, Active, etc.)
        def to_bool(val, default=True):
            if val is None or str(val).lower() == 'nan': return default
            return str(val).strip().lower() in ['true', '1', 'yes', 't', 'y', 'active']

        # 2. Helper for fuzzy column matching
        def get_fuzzy(row, keys, default=""):
            for k in keys:
                # Check original, lowercase, and underscored versions
                for variant in [k, k.lower(), k.lower().replace(" ", "_")]:
                    if variant in row:
                        val = row[variant]
                        return str(val).strip() if val is not None else default
            return default

        # 3. Extract and Clean
        raw_name = get_fuzzy(row, ["Name", "Full Name", "Employee Name", "EmpName_1"])
        eid = get_fuzzy(row, ["Employee ID", "ID", "Clock Number", "EID"])
        team = get_fuzzy(row, ["Team", "Group", "Crew"]).upper()
        role = get_fuzzy(row, ["Role", "Position", "Job Title", "JobTitle"]).upper()
        dept = get_fuzzy(row, ["Department", "Dept", "Area"]).upper()
        schedulable = to_bool(get_fuzzy(row, ["Schedulable", "Is Schedulable", "Active"]))

        # 4. Smart Name Splitting (Last, First Middle -> First, Last)
        first, last = "Unknown", "Unknown"
        if raw_name:
            if "," in raw_name:
                parts = raw_name.split(",", 1)
                last = parts[0].strip()
                # Handle potential middle names/initials in the first name part
                first_parts = parts[1].strip().split()
                first = first_parts[0] if first_parts else "Unknown"
            else:
                parts = raw_name.split()
                if len(parts) >= 2:
                    first = parts[0].strip()
                    last = parts[-1].strip()
                elif len(parts) == 1:
                    first = parts[0].strip()

        return {
            "employee_id": eid,
            "first_name": first,
            "last_name": last,
            "team": team,
            "role_type": role,
            "department": dept,
            "is_schedulable": schedulable
        }

    @staticmethod
    def normalize_name(name: str) -> str:
        """Standardizes names: 'Mullins, Tara' -> 'mullins tara'"""
        if not name: return ""
        name = str(name).lower()
        name = name.replace(",", " ")
        return " ".join(name.split()).strip()

    @staticmethod
    def upload_initial_roster(db: Session, site_id: str, roster_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Step 1: The Master Roster (Operational Truth)
        Defines teams, roles, and who belongs in the building.
        """
        created_count = 0
        updated_count = 0
        
        for raw_row in roster_data:
            # Normalize the row first!
            row = RosterService.normalize_row(raw_row)
            
            first = row['first_name']
            last = row['last_name']
            eid = row['employee_id']
            
            if not eid or eid.lower() == 'nan':
                eid = f"PLANT_{site_id[:4]}_{last.upper()}_{first.upper()}".replace(" ", "_")

            # Resolve Enums
            def get_enum(cls, val, default):
                if not val: return default
                v = str(val).strip()
                try: return cls(v)
                except:
                    try: return cls(v.upper())
                    except:
                        try: return cls(v.title())
                        except: return default

            raw_team = row['team']
            dept = get_enum(DepartmentType, row['department'], None)
            
            # Smart Department Inference
            if not dept or dept == DepartmentType.PACKING:
                if raw_team in ["A", "B", "C", "D", "AB"]:
                    dept = DepartmentType.SHIPPING
                elif raw_team in ["P1", "P2", "P3"]:
                    dept = DepartmentType.PACKING
                else:
                    dept = dept or DepartmentType.PACKING 

            role = get_enum(RoleType, row['role_type'], RoleType.GENERAL)
            is_schedulable = row['is_schedulable']

            # 3. Upsert
            emp = db.query(Employee).filter(Employee.employee_id == eid).first()
            if not emp:
                # Try fallback by name
                emp = db.query(Employee).filter(Employee.first_name == first, Employee.last_name == last, Employee.site_id == site_id).first()

            if emp:
                emp.employee_id = eid
                emp.department = dept
                emp.team = raw_team
                emp.role_type = role
                emp.is_schedulable = is_schedulable
                emp.active = True 
                updated_count += 1
            else:
                emp = Employee(
                    employee_id=eid,
                    site_id=site_id,
                    first_name=first,
                    last_name=last,
                    department=dept,
                    team=raw_team,
                    role_type=role,
                    is_schedulable=is_schedulable,
                    active=True
                )
                db.add(emp)
                created_count += 1
        
        db.commit()
        return {"created": created_count, "updated": updated_count}

    @staticmethod
    def reconcile_tempworks(db: Session, site_id: str, tw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Step 2: Sync TempWorks (Current Status)
        Matches names to Master Roster.
        - In Roster but NOT in TempWorks -> Mark Inactive (Termed)
        - In TempWorks but NOT in Roster -> Flag as New Hire
        """
        # 1. Load all Master Roster employees for this site
        roster_employees = db.query(Employee).filter(Employee.site_id == site_id).all()
        # Map: normalized_name -> Employee Object
        roster_map = {RosterService.normalize_name(f"{e.last_name} {e.first_name}"): e for e in roster_employees}
        
        # 2. Extract unique names from TempWorks file
        tw_names_seen = set()
        for row in tw_data:
            raw_name = row.get('full_name') or row.get('EmpName_1')
            if not raw_name: continue
            
            # Skip PTO/Admin noise
            job_title = str(row.get('jobtitle', '')).upper()
            if any(x in job_title for x in ["PTO", "BILLING", "MARKETING"]): continue
            
            norm_name = RosterService.normalize_name(raw_name)
            tw_names_seen.add(norm_name)

        # 3. Reconcile
        updated_count = 0
        termed_count = 0
        new_hires = []

        # Logic A: If in Roster but not in TempWorks -> Inactive
        for norm_name, emp in roster_map.items():
            if norm_name in tw_names_seen:
                emp.active = True
                updated_count += 1
            else:
                emp.active = False
                termed_count += 1
        
        # Logic B: If in TempWorks but not in Roster -> New Hire
        for tw_name in tw_names_seen:
            if tw_name not in roster_map:
                new_hires.append(tw_name.upper())

        db.commit()
        return {
            "updated_count": updated_count,
            "termed_count": termed_count,
            "new_hires": new_hires
        }
