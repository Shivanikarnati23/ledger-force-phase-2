from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
from app.models.salary import SalaryComponent, SalaryStructure, SalaryRevision

def get_employee_salary_structure(db: Session, employee_id: str, target_date: date):
    """
    Retrieves all active salary revisions or structures for an employee on a specific effective date.
    """
    revisions = db.query(SalaryRevision).filter(
        SalaryRevision.employee_id == employee_id,
        SalaryRevision.valid_from <= target_date,
        (SalaryRevision.valid_to == None) | (SalaryRevision.valid_to >= target_date)
    ).all()
    return revisions

def revise_employee_salary(db: Session, employee_id: str, component_id: str, new_amount: Decimal, valid_from: date, reason: str = None):
    """
    Closes the currently active salary revision for a component and creates a new revision.
    """
    current_revision = db.query(SalaryRevision).filter(
        SalaryRevision.employee_id == employee_id,
        SalaryRevision.component_id == component_id,
        SalaryRevision.valid_to == None
    ).first()
    
    if current_revision:
        current_revision.valid_to = valid_from

    new_revision = SalaryRevision(
        revision_id=f"REV-{employee_id}-{component_id}-{valid_from.strftime('%Y%m%d')}",
        employee_id=employee_id,
        component_id=component_id,
        amount=new_amount,
        valid_from=valid_from,
        valid_to=None
    )
    db.add(new_revision)
    db.commit()
    db.refresh(new_revision)
    return new_revision