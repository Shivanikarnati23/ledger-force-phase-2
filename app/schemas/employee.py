from pydantic import BaseModel, EmailStr
from typing import Optional

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    title: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department_id: Optional[int] = None
    role_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    department: Optional[DepartmentResponse] = None
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True