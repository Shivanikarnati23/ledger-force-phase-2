from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    department_id: str
    role_id: str
    manager_id: Optional[str] = None
    hire_date: Optional[date] = None

class EmployeeCreate(EmployeeBase):
    employee_id: str

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[str] = None
    role_id: Optional[str] = None
    manager_id: Optional[str] = None
    hire_date: Optional[date] = None
    exit_date: Optional[date] = None

class EmployeeResponse(EmployeeBase):
    employee_id: str
    exit_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)