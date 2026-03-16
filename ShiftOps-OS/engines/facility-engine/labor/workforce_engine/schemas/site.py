from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class SiteCreate(BaseModel):
    name: str

class SiteResponse(BaseModel):
    id: str
    name: str
    active: bool

    class Config:
        from_attributes = True

class LineCreate(BaseModel):
    name: str
    site_id: str
    department: str
    active: Optional[bool] = True

class LineResponse(BaseModel):
    id: str
    name: str
    site_id: str
    department: str
    active: bool

    class Config:
        from_attributes = True
