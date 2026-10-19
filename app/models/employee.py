from sqlalchemy import Column, String, Integer, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    department_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)

    employees = relationship("Employee", back_populates="department")
    assignments = relationship("EmployeeAssignment", back_populates="department")

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    level = Column(String, nullable=True)

    assignments = relationship("EmployeeAssignment", back_populates="role")

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    department_id = Column(String, ForeignKey("departments.department_id"), index=True, nullable=True)
    manager_id = Column(String, ForeignKey("employees.employee_id"), index=True, nullable=True)
    hire_date = Column(Date, nullable=False)
    exit_date = Column(Date, nullable=True)

    # Relationships
    department = relationship("Department", back_populates="employees")
    manager = relationship("Employee", remote_side=[employee_id], backref="direct_reports")
    assignments = relationship("EmployeeAssignment", back_populates="employee")

class EmployeeAssignment(Base):
    __tablename__ = "employee_assignments"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), index=True, nullable=False)
    department_id = Column(String, ForeignKey("departments.department_id"), index=True, nullable=False)
    role_id = Column(String, ForeignKey("roles.role_id"), index=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    employee = relationship("Employee", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    role = relationship("Role", back_populates="assignments")