from datetime import date
from sqlalchemy.orm import Session
from workforce_engine.models import Employee, Site
from workforce_engine.schemas.employee import EmployeeCreate


def create_employee(db: Session, employee_data: EmployeeCreate):

    # Validate site exists
    site = db.query(Site).filter(Site.id == employee_data.site_id).first()
    if not site:
        raise ValueError("Site does not exist")

    employee = Employee(
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        department=employee_data.department,
        team=employee_data.team,
        role_type=employee_data.role_type,
        site_id=employee_data.site_id,
        hire_date=employee_data.hire_date or date.today(),
        is_schedulable=employee_data.is_schedulable,
        is_fixed_role=employee_data.is_fixed_role
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee
