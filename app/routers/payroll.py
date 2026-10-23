from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

from app.database import get_db
from app.models.salary import SalaryStructure, SalaryRevision, SalaryComponent

router = APIRouter(prefix="/payroll", tags=["Salary & Compensation"])

class SalaryStructureResponse(BaseModel):
    structure_id: str
    employee_id: str
    component_id: Optional[str] = None
    base_salary: Decimal
    effective_date: date

    class Config:
        from_attributes = True

class SalaryRevisionResponse(BaseModel):
    revision_id: str
    employee_id: str
    component_id: str
    amount: Decimal
    valid_from: date
    valid_to: Optional[date] = None
    reason: Optional[str] = None  # Tracks the reason for each revision change

    class Config:
        from_attributes = True


@router.get("/structure/{employee_id}", response_model=SalaryStructureResponse)
def get_employee_salary_structure(
    employee_id: str, 
    as_of_date: Optional[date] = Query(None, description="Target date for effective dating lookup"),
    db: Session = Depends(get_db)
):
    target_date = as_of_date or date.today()
    
    query = select(SalaryStructure).where(
        and_(
            SalaryStructure.employee_id == employee_id,
            SalaryStructure.effective_date <= target_date
        )
    ).order_by(SalaryStructure.effective_date.desc())
    
    structure = db.execute(query).scalars().first()
    if not structure:
        raise HTTPException(status_code=404, detail="Salary structure not found for this employee on the given date.")
    
    return structure


@router.get("/revisions/{employee_id}", response_model=List[SalaryRevisionResponse])
def get_employee_salary_revisions(employee_id: str, db: Session = Depends(get_db)):
    query = select(SalaryRevision).where(SalaryRevision.employee_id == employee_id).order_by(SalaryRevision.valid_from.desc())
    revisions = db.execute(query).scalars().all()
    
    if not revisions:
        raise HTTPException(status_code=404, detail="No salary revision history found for this employee.")
        
    return revisions