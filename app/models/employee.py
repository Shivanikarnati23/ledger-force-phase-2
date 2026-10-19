from sqlalchemy import Column, String, Date, ForeignKey
from app.database import Base

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