from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Annotated
from pydantic import BeforeValidator
from workforce_engine.models import ScheduleAssignment, Employee, Shift, DepartmentType
from workforce_engine.database import get_db
from workforce_engine.services.assignment_service import generate_shipping_week, generate_packing_week
from workforce_engine.services.reporting_service import ReportingService

router = APIRouter(prefix="/schedule", tags=["Schedule"])

def to_title(v: str) -> str:
    if isinstance(v, str):
        return v.title()
    return v

CaseInsensitiveDepartmentType = Annotated[DepartmentType, BeforeValidator(to_title)]


@router.get("/weekly-grid")
def get_weekly_grid(
    department: CaseInsensitiveDepartmentType,
    week_start: date = Query(...),
    db: Session = Depends(get_db)
):
    try:
        return ReportingService.build_weekly_grid(db, department, week_start)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/shipping")
def generate_shipping_schedule(
    site_id: str,
    start_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    try:
        generate_shipping_week(db, site_id, start_date)
        return {"status": "shipping week generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/packing")
def generate_packing_schedule(
    site_id: str,
    start_date: datetime = Query(...),
    headcount: int = Query(None),
    db: Session = Depends(get_db)
):
    try:
        generate_packing_week(db, site_id, start_date, headcount_override=headcount)
        return {"status": "packing week generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_schedule(
    site_id: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    results = (
        db.query(ScheduleAssignment)
        .join(Employee)
        .join(Shift)
        .filter(Employee.site_id == site_id)
        .filter(ScheduleAssignment.scheduled_date >= start_date)
        .filter(ScheduleAssignment.scheduled_date <= end_date)
        .all()
    )

    schedule = []

    for row in results:
        shift_start = row.scheduled_date.replace(
            hour=row.shift.start_hour,
            minute=row.shift.start_minute,
            second=0,
            microsecond=0
        )
        shift_end = shift_start + timedelta(minutes=row.shift.duration_minutes)

        schedule.append({
            "employee_id": row.employee.id,
            "employee_name": f"{row.employee.first_name} {row.employee.last_name}",
            "shift_name": row.shift.name,
            "start": shift_start,
            "end": shift_end
        })

    return schedule
