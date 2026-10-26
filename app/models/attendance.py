from sqlalchemy import Column, Integer, Date, DateTime, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)  # e.g., 'Present', 'WFH', 'Absent', 'Late', 'MISSING_CHECKOUT'
    overtime_hours = Column(Float, default=0.0)

    # Relationship back to Employee model
    employee = relationship("Employee", back_populates="attendance_records")