from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., 'Casual', 'Sick', 'Earned'
    description = Column(String, nullable=True)


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    year = Column(Integer, nullable=False)
    allocated_days = Column(Float, nullable=False)
    used_days = Column(Float, default=0.0)
    remaining_days = Column(Float, nullable=False)

    employee = relationship("Employee", back_populates="leave_balances")
    leave_type = relationship("LeaveType")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Float, nullable=False)
    status = Column(String, default="applied")  # 'applied', 'approved', 'rejected'

    employee = relationship("Employee", back_populates="leave_requests")
    leave_type = relationship("LeaveType")