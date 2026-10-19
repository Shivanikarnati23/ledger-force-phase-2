from datetime import date
from decimal import Decimal
from sqlalchemy import text
from app.database import SessionLocal
from app.models.employee import Employee
from app.models.salary import SalaryComponent, SalaryRevision
from app.services.salary_service import get_employee_salary_structure, revise_employee_salary

def setup_clean_test_db(db):
    # Clean up test records safely
    db.execute(text("DELETE FROM salary_revisions"))
    db.execute(text("DELETE FROM salary_components"))
    db.execute(text("DELETE FROM employees WHERE employee_id = 'EMP-001'"))
    db.commit()

    # Insert test employee with a string department_id directly (no departments table needed)
    db.execute(text("""
        INSERT INTO employees (employee_id, first_name, last_name, email, department_id, role_id, hire_date)
        VALUES ('EMP-001', 'Test', 'User', 'test.user@example.com', 'DEPT-001', 'ROLE-DEV', '2023-01-01')
    """))
    db.commit()

    # Insert test salary component if not already present
    db.execute(text("""
        INSERT INTO salary_components (component_id, name) 
        VALUES ('COMP-BASIC', 'Basic Salary') 
        ON CONFLICT (component_id) DO NOTHING
    """))
    db.commit()

    employee = db.query(Employee).filter_by(employee_id='EMP-001').first()
    component = db.query(SalaryComponent).filter_by(component_id='COMP-BASIC').first()
    return employee, component

def test_effective_dated_salary_lookup():
    db = SessionLocal()
    try:
        employee, _ = setup_clean_test_db(db)
        target_date = date(2025, 6, 15)
        structure = get_employee_salary_structure(db, employee.employee_id, target_date)
        
        assert isinstance(structure, list)
    finally:
        db.close()

def test_salary_revision():
    db = SessionLocal()
    try:
        employee, component = setup_clean_test_db(db)
        new_amount = Decimal("75000.00")
        revision_date = date(2026, 1, 1)
        
        new_rev = revise_employee_salary(
            db=db,
            employee_id=employee.employee_id,
            component_id=component.component_id,
            new_amount=new_amount,
            valid_from=revision_date,
            reason="Annual Performance Increment"
        )
        
        assert new_rev is not None
        assert new_rev.amount == new_amount
        assert new_rev.valid_from == revision_date
        assert new_rev.valid_to is None
    finally:
        db.close()