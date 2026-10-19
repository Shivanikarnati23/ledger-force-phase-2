from sqlalchemy.orm import Session
from app.models.employee import Department, Role, Employee
from app.schemas.employee import DepartmentCreate, RoleCreate, EmployeeCreate

class EmployeeService:
    @staticmethod
    def create_department(db: Session, department: DepartmentCreate):
        db_dept = Department(name=department.name)
        db.add(db_dept)
        db.commit()
        db.refresh(db_dept)
        return db_dept

    @staticmethod
    def create_role(db: Session, role: RoleCreate):
        db_role = Role(title=role.title)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role

    @staticmethod
    def create_employee(db: Session, employee: EmployeeCreate):
        db_emp = Employee(**employee.dict())
        db.add(db_emp)
        db.commit()
        db.refresh(db_emp)
        return db_emp

    @staticmethod
    def get_employees(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Employee).offset(skip).limit(limit).all()