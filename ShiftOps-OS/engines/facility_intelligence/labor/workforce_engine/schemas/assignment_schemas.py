from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


from typing import Optional

class AssignmentCreate(BaseModel):
    employee_id: UUID
    shift_id: UUID
    line_id: Optional[UUID] = None
    scheduled_date: datetime


class AssignmentResponse(BaseModel):
    id: UUID
    employee_id: UUID
    shift_id: UUID
    line_id: Optional[UUID]
    scheduled_date: datetime
    created_at: datetime
    is_conflict: bool

    class Config:
        from_attributes = True
