import uuid
from datetime import datetime, timedelta, date
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from workforce_engine.models import (
    ScheduleAssignment, ConflictLog, Shift, Employee, 
    ScheduleParam, Position, Line, RiskLog, PositionType,
    EmploymentStatus, DepartmentType, EmployeeAvailability, AvailabilityStatus,
    RoleType
)
from workforce_engine.services.experience_service import ExperienceService
from workforce_engine.config import settings


def get_employee_hours_last_4_weeks(db: Session, employee_id: str, target_date: date) -> float:
    """Calculates total hours assigned to an employee in the 28 days preceding the target date."""
    # Ensure target_date is a datetime for comparison if needed, 
    # but here we can just use the date part if assignments are per-day.
    # Actually, scheduled_date is DateTime in the model.
    
    start_search = datetime.combine(target_date - timedelta(days=28), datetime.min.time())
    end_search = datetime.combine(target_date, datetime.min.time())

    assignments = db.query(ScheduleAssignment).filter(
        ScheduleAssignment.employee_id == employee_id,
        ScheduleAssignment.scheduled_date >= start_search,
        ScheduleAssignment.scheduled_date < end_search
    ).all()

    total_minutes = sum(a.shift.duration_minutes for a in assignments if a.shift)
    return total_minutes / 60.0


def is_employee_available(db: Session, employee_id: str, target_date: date) -> bool:
    """Checks if an employee is available for a given date."""
    record = db.query(EmployeeAvailability).filter(
        EmployeeAvailability.employee_id == employee_id,
        EmployeeAvailability.date == target_date,
        EmployeeAvailability.status != AvailabilityStatus.AVAILABLE
    ).first()
    return record is None


def _internal_generate_assignment(db: Session, emp: Optional[Employee], shift: Shift, scheduled_date: datetime, site_id: str, pos: Position = None):
    """Base assignment utility. Handles creation and conflict detection. Supports emp=None for OPEN slots."""
    new_assignment = ScheduleAssignment(
        id=str(uuid.uuid4()),
        employee_id=emp.id if emp else None,
        shift_id=shift.id,
        position_id=pos.id if pos else None,
        line_id=pos.line_id if pos else None,
        scheduled_date=scheduled_date,
        created_at=datetime.utcnow(),
        is_conflict=False
    )

    db.add(new_assignment)
    db.flush() 

    if not emp:
        return # No conflict checking for OPEN slots

    # Conflict Check (Simple overlap check)
    new_start = scheduled_date.replace(hour=shift.start_hour, minute=shift.start_minute, second=0, microsecond=0)
    new_end = new_start + timedelta(minutes=shift.duration_minutes)

    date_minus = scheduled_date - timedelta(days=1)
    date_plus = scheduled_date + timedelta(days=1)
    
    existing_conflicts = db.query(ScheduleAssignment).filter(
        ScheduleAssignment.employee_id == emp.id,
        ScheduleAssignment.id != new_assignment.id,
        ScheduleAssignment.scheduled_date.between(date_minus, date_plus)
    ).all()

    is_conflict = False
    for existing in existing_conflicts:
        ex_shift = existing.shift
        if not ex_shift: continue
        
        ex_start = existing.scheduled_date.replace(hour=ex_shift.start_hour, minute=ex_shift.start_minute, second=0, microsecond=0)
        ex_end = ex_start + timedelta(minutes=ex_shift.duration_minutes)

        if new_start < ex_end and new_end > ex_start:
            is_conflict = True
            log = ConflictLog(
                id=str(uuid.uuid4()),
                employee_id=emp.id,
                site_id=site_id,
                new_assignment_id=new_assignment.id,
                conflicting_assignment_id=existing.id,
                conflict_type="TIME_OVERLAP"
            )
            db.add(log)
    
    if is_conflict:
        new_assignment.is_conflict = True


def _allocate_packing_day(db: Session, site_id: str, current_date: datetime, shift: Shift, assigned_pool: List[Employee], headcount_limit: int = None):
    """Assigns employees to packing seats, filling missing ones with OPEN."""
    is_weekend = (current_date.weekday() + 1) % 7 in [0, 6]

    # Fairness Logic: Sort by hours in last 4 weeks, then by ID for deterministic tiebreak
    # We do this for the whole pool before splitting into veterans/new_hires
    scored_pool = []
    for e in assigned_pool:
        hours = get_employee_hours_last_4_weeks(db, e.id, current_date.date())
        scored_pool.append((hours, e.id, e))
    
    # Sort by hours (primary) and id (secondary)
    scored_pool.sort(key=lambda x: (x[0], x[1]))
    sorted_assigned_pool = [x[2] for x in scored_pool]

    veterans = [e for e in sorted_assigned_pool if not e.is_new]
    new_hires = [e for e in sorted_assigned_pool if e.is_new]

    def pull_employee():
        if veterans: return veterans.pop(0)
        if new_hires: return new_hires.pop(0)
        return None

    # Fetch positions
    all_pos = db.query(Position).filter(Position.site_id == site_id, Position.department == "Packing")
    if is_weekend:
        all_pos = all_pos.filter(Position.is_weekend_active == True)
    positions = all_pos.all()

    # Apply headcount limit if provided
    if headcount_limit is not None:
        positions = positions[:headcount_limit]

    for pos in positions:
        emp = pull_employee()
        _internal_generate_assignment(db, emp, shift, current_date, site_id, pos)


def _allocate_shipping_day(db: Session, site_id: str, current_date: datetime, shift: Shift, team_employees: List[Employee]):
    """
    Core Shipping Allocation Logic:
    1. Fill 18 required seats precisely.
    2. Match roles (Supervisor, Logistics, etc.) first.
    3. If < 18 people, leave remaining core seats OPEN.
    4. If > 18 people, assign extras as Floating.
    """
    # 1. Get all 18 positions for this shift
    all_positions = db.query(Position).filter(
        Position.site_id == site_id, 
        Position.department == "Shipping"
    ).all()

    # Define Role Priority for matching
    role_priority = [RoleType.SUPERVISOR, RoleType.LOGISTICS, RoleType.LINE_LEAD, RoleType.SR_DOCK]
    
    # Sort positions so we fill leadership roles first
    def get_pos_priority(p):
        if p.required_role_type == RoleType.SUPERVISOR: return 0
        if p.required_role_type == RoleType.LOGISTICS: return 1
        if p.required_role_type == RoleType.LINE_LEAD: return 2
        if p.required_role_type == RoleType.SR_DOCK: return 3
        if p.position_type == PositionType.SHIPPING_FIXED: return 4
        return 10
    
    sorted_positions = sorted(all_positions, key=get_pos_priority)
    
    # 2. Prepare Employee Pool
    # Sort: Leadership roles first, then by seniority (hire date)
    pool = sorted(team_employees, key=lambda x: (x.role_type not in role_priority, x.hire_date or date.max))
    
    assigned_emp_ids = set()
    
    # 3. Match Specific Roles First (Surgical Match)
    # We want to make sure Melissa (A Supervisor) actually gets the Supervisor seat.
    filled_positions = {} # pos_id -> emp_id
    
    for pos in sorted_positions:
        if pos.required_role_type in role_priority:
            # Try to find an exact role match in the pool
            match = next((e for e in pool if e.role_type == pos.required_role_type and e.id not in assigned_emp_ids), None)
            if match:
                filled_positions[pos.id] = match
                assigned_emp_ids.add(match.id)

    # 4. Fill Remaining Core Seats (Priority Order)
    for pos in sorted_positions:
        if pos.id in filled_positions:
            continue
        
        # Pull next available employee regardless of role
        emp = next((e for e in pool if e.id not in assigned_emp_ids), None)
        if emp:
            filled_positions[pos.id] = emp
            assigned_emp_ids.add(emp.id)
        else:
            # No more employees? This core seat stays OPEN
            filled_positions[pos.id] = None

    # 5. Execute Assignments for the 18 Core Seats
    for pos_id, emp in filled_positions.items():
        pos = next(p for p in all_positions if p.id == pos_id)
        _internal_generate_assignment(db, emp, shift, current_date, site_id, pos)

    # 6. Handle Overstaffing (Surplus)
    # Any employees left in the pool go to "Floating"
    remaining_emps = [e for e in pool if e.id not in assigned_emp_ids]
    if remaining_emps:
        # Assign to the 'Floating Position' slots (we have 2 in the DB, but can assign many to them)
        float_pos = next((p for p in all_positions if "Floating" in p.position_label), all_positions[-1])
        for extra_emp in remaining_emps:
            _internal_generate_assignment(db, extra_emp, shift, current_date, site_id, float_pos)


def generate_shipping_week(db: Session, site_id: str, start_date: datetime):
    end_date = start_date + timedelta(days=7)
    shipping_teams = ["A", "B", "C", "D"]
    
    # Clear existing assignments for this department/site/week (including OPEN slots)
    pos_ids = select(Position.id).where(
        Position.site_id == site_id,
        Position.department == "Shipping"
    ).scalar_subquery()

def generate_shipping_week(db: Session, site_id: str, start_date: datetime):
    # Snap to preceding Sunday
    days_to_subtract = (start_date.weekday() + 1) % 7
    actual_start = (start_date - timedelta(days=days_to_subtract)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = actual_start + timedelta(days=7)
    
    shipping_teams = list(SHIPPING_TEMPLATES.keys())
    
    # Clear existing
    emp_ids = select(Employee.id).where(Employee.site_id == site_id, Employee.team.in_(shipping_teams))
    db.query(ScheduleAssignment).filter(
        ScheduleAssignment.position_id.in_(pos_ids),
        ScheduleAssignment.scheduled_date >= start_date,
        ScheduleAssignment.scheduled_date < end_date
    ).delete(synchronize_session=False)

    shifts = {
        "DAY_FULL": db.query(Shift).filter(Shift.name == "Shipping Day Full").first(),
        "NIGHT_FULL": db.query(Shift).filter(Shift.name == "Shipping Night Full").first(),
        "WED_AM": db.query(Shift).filter(Shift.name == "Shipping Wed AM Split").first(),
        "WED_PM": db.query(Shift).filter(Shift.name == "Shipping Wed PM Split").first(),
        "WED_NIGHT_EARLY": db.query(Shift).filter(Shift.name == "Shipping Wed Night Early").first(),
        "WED_NIGHT_LATE": db.query(Shift).filter(Shift.name == "Shipping Wed Night Late").first(),
    }

    employees = db.query(Employee).filter(
        Employee.site_id == site_id,
        Employee.team.in_(shipping_teams), 
        Employee.employment_status == EmploymentStatus.ACTIVE,
        Employee.is_schedulable == True
    ).all()

    for day_offset in range(7):
        current_date = start_date + timedelta(days=day_offset)
        day_of_week = (current_date.weekday() + 1) % 7 # 0=Sun, 1=Mon... 6=Sat

        work_plan = {}
        if day_of_week in [0, 1, 2]: # Sun-Tue
            work_plan["A"] = shifts["DAY_FULL"]
            work_plan["C"] = shifts["NIGHT_FULL"]
        elif day_of_week == 3: # Wed Split (The changeover)
            work_plan["A"] = shifts["WED_AM"]
            work_plan["B"] = shifts["WED_PM"]
            work_plan["C"] = shifts["WED_NIGHT_EARLY"]
            work_plan["D"] = shifts["WED_NIGHT_LATE"]
        elif day_of_week in [4, 5, 6]: # Thu-Sat
            work_plan["B"] = shifts["DAY_FULL"]
            work_plan["D"] = shifts["NIGHT_FULL"]

        for team, shift in work_plan.items():
            if not shift: continue
            team_emps = [e for e in employees if e.team == team and is_employee_available(db, e.id, current_date.date())]
            _allocate_shipping_day(db, site_id, current_date, shift, team_emps)

    # Post-generation risk validation
    for d in range(7):
        validate_experience_risk(db, site_id, start_date + timedelta(days=d))

    db.commit()


def generate_packing_week(db: Session, site_id: str, start_date: datetime, headcount_override: int = None):
    end_date = start_date + timedelta(days=7)
    packing_teams = ["P1", "P2", "P3"]
    
    # Clear existing assignments for this department/site/week (including OPEN slots)
    pos_ids = select(Position.id).where(
        Position.site_id == site_id,
        Position.department == "Packing"
    ).scalar_subquery()

    db.query(ScheduleAssignment).filter(
        ScheduleAssignment.position_id.in_(pos_ids),
        ScheduleAssignment.scheduled_date >= start_date,
        ScheduleAssignment.scheduled_date < end_date
    ).delete(synchronize_session=False)

    shift_map = {
        "P1": db.query(Shift).filter(Shift.name == "Packer P1").first(),
        "P2": db.query(Shift).filter(Shift.name == "Packer P2").first(),
        "P3": db.query(Shift).filter(Shift.name == "Packer P3").first(),
    }

    for day_offset in range(7):
        current_date = start_date + timedelta(days=day_offset)
        for team_label, shift in shift_map.items():
            if not shift: continue
            available_emps = db.query(Employee).filter(
                Employee.site_id == site_id, 
                Employee.department == DepartmentType.PACKING,
                Employee.team == team_label, 
                Employee.employment_status == EmploymentStatus.ACTIVE, 
                Employee.is_schedulable == True
            ).all()
            
            valid_emps = [e for e in available_emps if is_employee_available(db, e.id, current_date.date())]
            _allocate_packing_day(db, site_id, current_date, shift, valid_emps, headcount_limit=headcount_override)

    # Post-generation risk validation
    for d in range(7):
        validate_experience_risk(db, site_id, start_date + timedelta(days=d))

    db.commit()


def validate_experience_risk(db: Session, site_id: str, target_date: datetime):
    """
    Runs post-generation validation and logs risks to RiskLog table.
    """
    report = ExperienceService.get_assignment_risk_report(db, target_date.date())

    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    # Clear old risks for this day
    db.query(RiskLog).filter(
        RiskLog.site_id == site_id,
        RiskLog.detected_at >= day_start,
        RiskLog.detected_at < day_end
    ).delete()

    for shift_entry in report["shifts"]:
        for line_entry in shift_entry["lines"]:
            if line_entry["risk_level"] in ["YELLOW", "RED"]:
                risk_msg = f"Line {line_entry['line_name']} has {line_entry['concentration_pct']}% new hires."
                if line_entry["critical_breaches"]:
                    risk_msg += f" {len(line_entry['critical_breaches'])} Critical Position breach(es)."

                log = RiskLog(
                    id=str(uuid.uuid4()),
                    site_id=site_id,
                    level="LINE",
                    entity_id=line_entry["line_id"],
                    risk_type="CONCENTRATION" if not line_entry["critical_breaches"] else "CRITICAL_POSITION",
                    risk_level=line_entry["risk_level"],
                    message=risk_msg,
                    detected_at=datetime.utcnow()
                )
                db.add(log)

        if "RED" in shift_entry["shift_risk_score"]:
            log = RiskLog(
                id=str(uuid.uuid4()),
                site_id=site_id,
                level="SHIFT",
                entity_id=shift_entry["shift_id"],
                risk_type="AGGREGATE",
                risk_level="RED",
                message=f"Shift {shift_entry['shift_name']} is at HIGH RISK due to line imbalances.",
                detected_at=datetime.utcnow()
            )
            db.add(log)

    db.commit()
