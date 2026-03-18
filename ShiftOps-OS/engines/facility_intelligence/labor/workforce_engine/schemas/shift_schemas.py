from pydantic import BaseModel
from uuid import UUID


class ShiftCreate(BaseModel):
    site_id: str
    name: str
    start_hour: int
    start_minute: int
    duration_minutes: int
