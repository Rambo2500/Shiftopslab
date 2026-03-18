from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from workforce_engine.database import get_db
from workforce_engine.models import ScheduleAssignment, Shift
from workforce_engine.schemas.assignment_schemas import AssignmentCreate

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/")
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db)
):
    # Fetch shift
    new_shift = db.query(Shift).filter(Shift.id == str(payload.shift_id)).first()
    if not new_shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    # Compute new shift window
    new_start = payload.scheduled_date.replace(
        hour=new_shift.start_hour,
        minute=new_shift.start_minute,
        second=0,
        microsecond=0
    )

    new_end = new_start + timedelta(minutes=new_shift.duration_minutes)

    # Fetch existing assignments for employee on adjacent dates to catch overnight shifts
    date_minus = payload.scheduled_date - timedelta(days=1)
    date_plus = payload.scheduled_date + timedelta(days=1)

    existing_assignments = (
        db.query(ScheduleAssignment)
        .filter(ScheduleAssignment.employee_id == str(payload.employee_id))
        .filter(
            ScheduleAssignment.scheduled_date.between(
                date_minus,
                date_plus
            )
        )
        .all()
    )

    for assignment in existing_assignments:
        existing_shift = db.query(Shift).filter(Shift.id == assignment.shift_id).first()

        existing_start = assignment.scheduled_date.replace(
            hour=existing_shift.start_hour,
            minute=existing_shift.start_minute,
            second=0,
            microsecond=0
        )

        existing_end = existing_start + timedelta(minutes=existing_shift.duration_minutes)

        # Overlap check
        if new_start < existing_end and new_end > existing_start:
            raise HTTPException(
                status_code=400,
                detail="Schedule conflict: overlapping shift detected."
            )

    # If no conflicts, create assignment
    assignment = ScheduleAssignment(
        employee_id=str(payload.employee_id),
        shift_id=str(payload.shift_id),
        scheduled_date=payload.scheduled_date
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment
