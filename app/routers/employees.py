from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.employee import (
    DepartmentCreate, DepartmentResponse,
    RoleCreate, RoleResponse,
    EmployeeCreate, EmployeeResponse
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    return EmployeeService.create_department(db=db, department=department)

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return EmployeeService.create_role(db=db, role=role)

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return EmployeeService.create_employee(db=db, employee=employee)

@router.get("/", response_model=List[EmployeeResponse])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return EmployeeService.get_employees(db=db, skip=skip, limit=limit)