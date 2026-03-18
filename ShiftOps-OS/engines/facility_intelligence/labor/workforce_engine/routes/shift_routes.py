from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from workforce_engine.database import get_db
from workforce_engine.models import Shift
from workforce_engine.schemas.shift_schemas import ShiftCreate

router = APIRouter(prefix="/shifts", tags=["Shifts"])


@router.post("/")
def create_shift(payload: ShiftCreate, db: Session = Depends(get_db)):

    shift = Shift(
        site_id=str(payload.site_id),
        name=payload.name,
        start_hour=payload.start_hour,
        start_minute=payload.start_minute,
        duration_minutes=payload.duration_minutes
    )

    db.add(shift)
    db.commit()
    db.refresh(shift)

    return shift
