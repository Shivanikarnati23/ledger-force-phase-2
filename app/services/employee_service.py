from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.salary import SalaryRevision, SalaryComponent

def get_employee_salary_structure(db: Session, employee_id: str, target_date: date):
    """
    Retrieves all active salary revisions for an employee on a specific effective date.
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
    # 1. Find the current active revision for this employee and component
    current_revision = db.query(SalaryRevision).filter(
        SalaryRevision.employee_id == employee_id,
        SalaryRevision.component_id == component_id,
        SalaryRevision.valid_to == None
    ).first()

    if current_revision:
        # Close the previous record the day before the new one starts
        current_revision.valid_to = valid_from - timedelta(days=1)
        db.add(current_revision)

    # 2. Insert the new salary revision
    new_revision_id = f"REV-{employee_id}-{component_id}-{valid_from.strftime('%Y%m%d')}"
    new_revision = SalaryRevision(
        revision_id=new_revision_id,
        employee_id=employee_id,
        component_id=component_id,
        amount=Decimal(str(new_amount)),  # Ensure precise Decimal handling
        valid_from=valid_from,
        valid_to=None,  # Null indicates currently active
        reason=reason
    )
    db.add(new_revision)
    db.commit()
    db.refresh(new_revision)
    
    return new_revision