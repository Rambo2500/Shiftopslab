import unittest
from datetime import date, timedelta
from workforce_engine.models import Employee
from workforce_engine.services.experience_service import ExperienceService
from workforce_engine.config import settings

class TestExperienceLogic(unittest.TestCase):
    def test_veteran_status(self):
        # 100 days ago should be a veteran (threshold 90)
        hire_date = date.today() - timedelta(days=100)
        emp = Employee(hire_date=hire_date)
        status = ExperienceService.get_employee_experience_status(emp, date.today())
        self.assertEqual(status, "VETERAN")

    def test_new_status(self):
        # 10 days ago should be NEW
        hire_date = date.today() - timedelta(days=10)
        emp = Employee(hire_date=hire_date)
        status = ExperienceService.get_employee_experience_status(emp, date.today())
        self.assertEqual(status, "NEW")

    def test_future_hire_is_new(self):
        # Hired tomorrow is NEW (Edge case)
        hire_date = date.today() + timedelta(days=1)
        emp = Employee(hire_date=hire_date)
        status = ExperienceService.get_employee_experience_status(emp, date.today())
        self.assertEqual(status, "NEW")

    def test_null_hire_date_is_new(self):
        # No hire date should default to NEW for safety
        emp = Employee(hire_date=None)
        status = ExperienceService.get_employee_experience_status(emp, date.today())
        self.assertEqual(status, "NEW")

if __name__ == "__main__":
    unittest.main()
