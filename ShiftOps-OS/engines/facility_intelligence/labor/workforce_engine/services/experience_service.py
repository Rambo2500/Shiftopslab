from datetime import date, timedelta
from typing import List, Dict, Any, DefaultDict
from collections import defaultdict
from sqlalchemy.orm import Session
from workforce_engine.models import Employee, ScheduleAssignment, Position, Line, Shift
from workforce_engine.config import settings

class ExperienceService:

    @staticmethod
    def get_employee_experience_status(employee: Employee, reference_date: date) -> str:
        """
        Returns 'NEW' if the employee has less than threshold days of experience
        as of the reference_date, otherwise 'VETERAN'.
        """
        if not employee or not employee.hire_date:
            return "NEW"
        
        # Ensure we are comparing dates
        hire_date = employee.hire_date
        if hasattr(hire_date, 'date'):
            hire_date = hire_date.date()

        if hire_date > reference_date:
            return "NEW"

        if (reference_date - hire_date).days < settings.EXPERIENCE_THRESHOLD_DAYS:
            return "NEW"
        return "VETERAN"

    @staticmethod
    def get_assignment_risk_report(db: Session, target_date: date) -> Dict[str, Any]:
        """
        Analyzes assignments for a specific date and returns a structural risk report.
        """
        # Fetch all assignments with related data, including OPEN slots (outerjoin Employee)
        assignments = (
            db.query(ScheduleAssignment)
            .outerjoin(Employee)
            .join(Position)
            .join(Line)
            .join(Shift)
            .filter(
                ScheduleAssignment.scheduled_date >= target_date,
                ScheduleAssignment.scheduled_date < target_date + timedelta(days=1)
            )
            .all()
        )

        # Structure for aggregation: shift_id -> line_id -> list of assignments
        structural_data: DefaultDict[str, DefaultDict[str, List[ScheduleAssignment]]] = defaultdict(lambda: defaultdict(list))
        
        shift_names = {}
        line_names = {}

        for a in assignments:
            structural_data[a.shift_id][a.line_id].append(a)
            shift_names[a.shift_id] = a.shift.name if a.shift else "UNKNOWN SHIFT"
            line_names[a.line_id] = a.line.name if a.line else "UNKNOWN LINE"

        shifts_report = []
        total_new = 0
        total_veteran = 0

        for shift_id, lines in structural_data.items():
            shift_entry = {
                "shift_id": shift_id,
                "shift_name": shift_names[shift_id],
                "lines": [],
                "shift_risk_score": "NONE"
            }
            
            shift_has_red = False
            shift_has_yellow = False

            for line_id, line_assignments in lines.items():
                line_new_count = 0
                line_critical_new_count = 0
                critical_position_breaches = []
                assigned_count = 0

                for a in line_assignments:
                    if not a.employee:
                        continue # OPEN slots don't count towards experience risk
                    
                    assigned_count += 1
                    status = ExperienceService.get_employee_experience_status(a.employee, target_date)
                    if status == "NEW":
                        line_new_count += 1
                        total_new += 1
                        if a.position.is_critical:
                            line_critical_new_count += 1
                            critical_position_breaches.append({
                                "employee_name": f"{a.employee.first_name} {a.employee.last_name}",
                                "position_label": a.position.position_label
                            })
                    else:
                        total_veteran += 1

                concentration = line_new_count / assigned_count if assigned_count > 0 else 0
                
                # Determine Line Risk
                line_risk = "GREEN"
                if concentration >= settings.RED_RISK_THRESHOLD or line_critical_new_count > 0:
                    line_risk = "RED"
                    shift_has_red = True
                elif concentration >= settings.YELLOW_RISK_THRESHOLD:
                    line_risk = "YELLOW"
                    shift_has_yellow = True

                shift_entry["lines"].append({
                    "line_id": line_id,
                    "line_name": line_names[line_id],
                    "concentration_pct": round(concentration * 100, 2),
                    "new_count": line_new_count,
                    "assigned_count": assigned_count,
                    "total_seats": len(line_assignments),
                    "risk_level": line_risk,
                    "critical_breaches": critical_position_breaches
                })

            # Aggregated Shift Risk
            if shift_has_red:
                shift_entry["shift_risk_score"] = "HIGH (RED)"
            elif shift_has_yellow:
                shift_entry["shift_risk_score"] = "MODERATE (YELLOW)"
            else:
                shift_entry["shift_risk_score"] = "LOW (GREEN)"

            shifts_report.append(shift_entry)

        total_assignments = total_new + total_veteran
        overall_concentration = total_new / total_assignments if total_assignments > 0 else 0

        return {
            "date": target_date.isoformat(),
            "summary": {
                "total_assignments": total_assignments,
                "total_new": total_new,
                "total_veteran": total_veteran,
                "overall_new_concentration_pct": round(overall_concentration * 100, 2)
            },
            "shifts": shifts_report
        }
