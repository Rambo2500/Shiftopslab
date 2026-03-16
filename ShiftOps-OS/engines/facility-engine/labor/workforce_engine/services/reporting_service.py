from datetime import date, timedelta
from typing import List, Dict, Any, DefaultDict
from collections import defaultdict
from sqlalchemy.orm import Session
from workforce_engine.models import (
    Employee, ScheduleAssignment, Shift, DepartmentType
)

class ReportingService:

    @staticmethod
    def build_weekly_grid(db: Session, department: DepartmentType, week_start: date) -> Dict[str, Any]:
        """
        Pivots daily assignments into an employee-centric weekly grid.
        Includes OPEN slots for vacant seats.
        """
        # Force start to Sunday
        days_to_subtract = (week_start.weekday() + 1) % 7
        actual_start = week_start - timedelta(days=days_to_subtract)
        actual_end = actual_start + timedelta(days=7)
        
        # 1. Fetch all assignments for the week and department
        assignments = (
            db.query(ScheduleAssignment)
            .outerjoin(Employee)
            .join(Shift)
            .join(ScheduleAssignment.position) # Ensure we only get assignments for this department
            .filter(
                ScheduleAssignment.position.has(department=department.value),
                ScheduleAssignment.scheduled_date >= week_start,
                ScheduleAssignment.scheduled_date < week_end
            )
            .all()
        )

        # 2. Group by Team -> Employee
        # Structure: team_name -> employee_display_name -> { day_index: "time_range" }
        grid_data: DefaultDict[str, DefaultDict[str, Dict[int, str]]] = defaultdict(lambda: defaultdict(dict))
        
        # We also need to keep track of team for OPEN slots
        # Since ScheduleAssignment doesn't have a team, we'll infer it from the employees 
        # OR from the generation logic. For now, we'll use the employee's team or "OPEN"
        
        for a in assignments:
            if a.employee:
                team = a.employee.team or "UNKNOWN"
                emp_name = f"{a.employee.last_name}, {a.employee.first_name}"
            else:
                team = "OPEN_SLOTS" # Group all open slots together or by position
                emp_name = f"OPEN - {a.position.position_label}"
            
            day_idx = (a.scheduled_date.date() - week_start).days
            
            def fmt_time(total_minutes):
                h = (total_minutes // 60) % 24
                m = int(total_minutes % 60)
                suffix = "a" if h < 12 else "p"
                display_h = h if h <= 12 else h - 12
                if display_h == 0: display_h = 12
                return f"{int(display_h)}:{m:02d}{suffix}"

            start_total_min = a.shift.start_hour * 60 + a.shift.start_minute
            end_total_min = start_total_min + a.shift.duration_minutes
            time_str = f"{fmt_time(start_total_min)} - {fmt_time(end_total_min)}"
            grid_data[team][emp_name][day_idx] = time_str

        # 3. Final formatting
        teams_report = []
        sorted_teams = sorted(grid_data.keys())
        
        for team_name in sorted_teams:
            team_rows = []
            sorted_emps = sorted(grid_data[team_name].keys())
            for emp_name in sorted_emps:
                row = {"name": emp_name, "days": []}
                for d in range(7):
                    row["days"].append(grid_data[team_name][emp_name].get(d, ""))
                team_rows.append(row)
            teams_report.append({"team": team_name, "employees": team_rows})

        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        headers = [f"{day_names[d]} {(actual_start + timedelta(days=d)).strftime('%m/%d')}" for d in range(7)]

        return {
            "department": department.value,
            "week_range": f"{actual_start.strftime('%m/%d')} - {(actual_end - timedelta(days=1)).strftime('%m/%d')}",
            "days_header": headers,
            "teams": teams_report
        }
