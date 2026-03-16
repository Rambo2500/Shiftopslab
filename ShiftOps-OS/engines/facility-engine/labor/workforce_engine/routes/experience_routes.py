from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from workforce_engine.database import get_db
from workforce_engine.services.experience_service import ExperienceService

router = APIRouter(prefix="/experience", tags=["Experience"])

@router.get("/risk-report")
def get_experience_risk_report(
    target_date: date = Query(...),
    db: Session = Depends(get_db)
):
    """
    Returns a report highlighting assignments where 'NEW' employees are scheduled.
    This provides visibility into potential operational risks due to lack of experience.
    """
    try:
        report = ExperienceService.get_assignment_risk_report(db, target_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
