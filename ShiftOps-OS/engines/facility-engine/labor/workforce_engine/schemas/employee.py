from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from workforce_engine.models import AvailabilityStatus


class EmployeeAvailabilityCreate(BaseModel):
    employee_id: str
    target_date: date
    status: AvailabilityStatus
    reason: Optional[str] = None


class EmployeeAvailabilityResponse(BaseModel):
    id: str
    employee_id: str
    date: date
    status: AvailabilityStatus
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    department: str
    team: Optional[str] = None
    role_type: str
    site_id: str
    hire_date: Optional[datetime] = None
    is_schedulable: bool = True
    is_fixed_role: bool = False


class EmployeeResponse(BaseModel):
    id: str
    employee_id: Optional[str]
    first_name: str
    last_name: str
    department: str
    team: Optional[str]
    role_type: str
    site_id: str
    hire_date: Optional[datetime]
    is_new: bool
    is_schedulable: bool
    is_fixed_role: bool

    class Config:
        from_attributes = True
