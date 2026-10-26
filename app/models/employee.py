from sqlalchemy import Column, String, Date, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department_id = Column(String, nullable=False)
    role_id = Column(String, nullable=False)
    manager_id = Column(String, nullable=True)
    hire_date = Column(Date, nullable=False)
    exit_date = Column(Date, nullable=True)
    # Add these inside your Employee class:
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    leave_balances = relationship("LeaveBalance", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")