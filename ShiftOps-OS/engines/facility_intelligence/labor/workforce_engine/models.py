import enum
import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Date, Enum as SqlEnum
from sqlalchemy.orm import relationship

from .database import Base


class PositionType(str, enum.Enum):
    # Packing Types
    BREAK_RELIEF = "BREAK_RELIEF"
    MUFFIN_ANCHOR = "MUFFIN_ANCHOR"
    BREAD_BUN_ANCHOR = "BREAD_BUN_ANCHOR"
    PACKING_GENERAL = "PACKING_GENERAL"
    FLOATING = "FLOATING"
    
    # Shipping Types
    SHIPPING_FIXED = "SHIPPING_FIXED"
    SHIPPING_ROTATIONAL = "SHIPPING_ROTATIONAL"
    SHIPPING_DOCK = "SHIPPING_DOCK"


class DepartmentType(str, enum.Enum):
    SHIPPING = "Shipping"
    PACKING = "Packing"


class ShiftType(str, enum.Enum):
    DAY = "DAY"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    LOA = "LOA"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    PTO = "PTO"
    CALL_IN = "CALL_IN"
    TRAINING = "TRAINING"
    MEDICAL = "MEDICAL"


class RoleType(str, enum.Enum):
    SUPERVISOR = "SUPERVISOR"
    LOGISTICS = "LOGISTICS"
    LINE_LEAD = "LINE_LEAD"
    SR_DOCK = "SR_DOCK"
    GENERAL = "GENERAL"


def generate_uuid():
    return str(uuid.uuid4())


class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    active = Column(Boolean, default=True)


class Line(Base):
    __tablename__ = "lines"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    department = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    site = relationship("Site")


class Position(Base):
    __tablename__ = "positions"
    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"))
    line_id = Column(String, ForeignKey("lines.id"))
    department = Column(String)  # "Packing" or "Shipping" 
    position_label = Column(String) # "Position 1", "Break Relief", etc. 
    position_type = Column(SqlEnum(PositionType), nullable=True)
    required_role_type = Column(SqlEnum(RoleType), nullable=True)
    is_weekend_active = Column(Boolean, default=True)
    is_critical = Column(Boolean, default=False)

    site = relationship("Site")
    line = relationship("Line")


class ScheduleParam(Base):
    __tablename__ = "schedule_params"
    id = Column(Integer, primary_key=True, autoincrement=True)
    department = Column(String) # "Packing" or "Shipping" 
    day_of_week = Column(Integer) # 0=Sunday, 1=Monday... 
    required_headcount = Column(Integer) # 12, 14, or 16 


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, unique=True, index=True, nullable=True) # TempWorks ID
    site_id = Column(String, ForeignKey("sites.id"))
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    department = Column(SqlEnum(DepartmentType), nullable=True)
    team = Column(String(10), nullable=True) # A, B, C, D, P1, P2, P3
    shift_type = Column(SqlEnum(ShiftType), nullable=True)
    role_type = Column(SqlEnum(RoleType), default=RoleType.GENERAL)
    
    active = Column(Boolean, default=True)
    employment_status = Column(SqlEnum(EmploymentStatus), default=EmploymentStatus.ACTIVE)
    hire_date = Column(Date, nullable=True)
    is_rotating = Column(Boolean, default=True)
    is_schedulable = Column(Boolean, default=True) # James/Ashe = False
    is_fixed_role = Column(Boolean, default=False) # Supervisor/Logistics/LineLead = True

    site = relationship("Site")
    availabilities = relationship("EmployeeAvailability", back_populates="employee")

    @property
    def name(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def is_new(self):
        if not self.hire_date:
            return False
        return (date.today() - self.hire_date).days < 90

class FixedAssignment(Base):
    """Maps an employee to a permanent position (e.g. Supervisor A)"""
    __tablename__ = "fixed_assignments"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), unique=True)
    position_key = Column(String, unique=True) # e.g. "SUPERVISOR_A", "LOGISTICS_B"
    
    employee = relationship("Employee")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"))
    name = Column(String, nullable=False)

    start_hour = Column(Integer, nullable=False)
    start_minute = Column(Integer, nullable=False, default=0)

    duration_minutes = Column(Integer, nullable=False)

    site = relationship("Site")

class ScheduleAssignment(Base):
    __tablename__ = "schedule_assignments"

    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"))
    shift_id = Column(String, ForeignKey("shifts.id"))
    line_id = Column(String, ForeignKey("lines.id"))
    position_id = Column(String, ForeignKey("positions.id"))
    scheduled_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_conflict = Column(Boolean, default=False)

    employee = relationship("Employee")
    shift = relationship("Shift")
    line = relationship("Line")
    position = relationship("Position")


class ConflictLog(Base):
    __tablename__ = "conflict_logs"

    id = Column(String, primary_key=True, default=generate_uuid)

    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)

    new_assignment_id = Column(String, ForeignKey("schedule_assignments.id"))
    conflicting_assignment_id = Column(String, ForeignKey("schedule_assignments.id"))

    conflict_type = Column(String, nullable=False, default="TIME_OVERLAP")

    detected_at = Column(DateTime, default=datetime.utcnow)


class RiskLog(Base):
    __tablename__ = "risk_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    
    # Aggregation level (Shift or Line)
    level = Column(String, nullable=False) # "SHIFT" or "LINE"
    entity_id = Column(String, nullable=False) # shift_id or line_id
    
    risk_type = Column(String, nullable=False) # "CONCENTRATION" or "CRITICAL_POSITION"
    risk_level = Column(String, nullable=False) # "YELLOW" or "RED"
    
    message = Column(String, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)


class EmployeeAvailability(Base):
    __tablename__ = "employee_availabilities"

    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(SqlEnum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="availabilities")
