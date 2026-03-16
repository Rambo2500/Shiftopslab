import unittest
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from workforce_engine.models import Base, Employee, Shift, ScheduleAssignment, DepartmentType, RoleType, Site, Position, Line, PositionType
from workforce_engine.services.assignment_service import get_employee_hours_last_4_weeks, generate_packing_week

class TestFairnessLogic(unittest.TestCase):
    def setUp(self):
        # Use an in-memory SQLite for fast testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

        # Setup basic data
        self.site = Site(name="Test Site")
        self.db.add(self.site)
        self.db.flush()

        self.line = Line(name="Test Line", site_id=self.site.id, department="Packing")
        self.db.add(self.line)
        self.db.flush()

        # Create a standard shift (8 hours)
        self.shift = Shift(
            name="Packer P1", 
            site_id=self.site.id, 
            start_hour=8, 
            duration_minutes=480 # 8 hours
        )
        self.db.add(self.shift)
        self.db.add(Shift(name="Packer P2", site_id=self.site.id, start_hour=16, duration_minutes=480))
        self.db.add(Shift(name="Packer P3", site_id=self.site.id, start_hour=0, duration_minutes=480))
        
        # Create positions
        for i in range(1, 11):
            pos = Position(
                site_id=self.site.id,
                line_id=self.line.id,
                department="Packing",
                position_label=f"Pos {i}",
                position_type=PositionType.PACKING_GENERAL,
                required_role_type=RoleType.GENERAL
            )
            self.db.add(pos)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_fairness_hours_calculation(self):
        emp = Employee(
            first_name="Test", last_name="User", 
            site_id=self.site.id, department=DepartmentType.PACKING,
            role_type=RoleType.GENERAL, hire_date=date(2020,1,1)
        )
        self.db.add(emp)
        self.db.commit()

        target_date = date(2026, 3, 3)
        # Add 2 assignments in the last 2 weeks (16 hours)
        for i in range(1, 3):
            assign = ScheduleAssignment(
                employee_id=emp.id,
                shift_id=self.shift.id,
                scheduled_date=datetime.combine(target_date - timedelta(days=i*7), datetime.min.time())
            )
            self.db.add(assign)
        self.db.commit()

        hours = get_employee_hours_last_4_weeks(self.db, emp.id, target_date)
        self.assertEqual(hours, 16.0)

    def test_generator_selects_lowest_hours(self):
        # Create two employees
        emp_a = Employee(
            id="emp_a", first_name="High", last_name="Hours", 
            site_id=self.site.id, department=DepartmentType.PACKING,
            role_type=RoleType.GENERAL, hire_date=date(2020,1,1),
            team="P1", is_rotating=True
        )
        emp_b = Employee(
            id="emp_b", first_name="Low", last_name="Hours", 
            site_id=self.site.id, department=DepartmentType.PACKING,
            role_type=RoleType.GENERAL, hire_date=date(2020,1,1),
            team="P1", is_rotating=True
        )
        self.db.add_all([emp_a, emp_b])
        self.db.commit()

        target_date = datetime(2026, 3, 3)
        
        # Give Emp A some history (8 hours)
        assign = ScheduleAssignment(
            employee_id=emp_a.id,
            shift_id=self.shift.id,
            scheduled_date=target_date - timedelta(days=7)
        )
        self.db.add(assign)
        self.db.commit()

        # Run generator for 1 day with headcount 1
        # It should pick Emp B because B has 0 hours and A has 8.
        generate_packing_week(self.db, self.site.id, target_date, headcount_override=1)
        
        # Check assignment for the target date
        assignment = self.db.query(ScheduleAssignment).filter(
            ScheduleAssignment.scheduled_date == target_date
        ).first()

        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.employee_id, "emp_b")

    def test_deterministic_tiebreak(self):
        # Two employees with 0 hours
        # ID 'emp_a' should come before 'emp_b' alphabetically/lexicographically 
        # because of the `(hours, e.id)` sort key.
        emp_b = Employee(
            id="emp_b", first_name="User", last_name="B", 
            site_id=self.site.id, department=DepartmentType.PACKING,
            role_type=RoleType.GENERAL, team="P1", is_rotating=True
        )
        emp_a = Employee(
            id="emp_a", first_name="User", last_name="A", 
            site_id=self.site.id, department=DepartmentType.PACKING,
            role_type=RoleType.GENERAL, team="P1", is_rotating=True
        )
        self.db.add_all([emp_a, emp_b])
        self.db.commit()

        target_date = datetime(2026, 3, 3)
        generate_packing_week(self.db, self.site.id, target_date, headcount_override=1)

        assignment = self.db.query(ScheduleAssignment).filter(
            ScheduleAssignment.scheduled_date == target_date
        ).first()

        self.assertEqual(assignment.employee_id, "emp_a")

if __name__ == "__main__":
    unittest.main()
