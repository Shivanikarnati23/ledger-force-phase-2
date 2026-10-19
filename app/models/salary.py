from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from app.database import Base

class SalaryComponent(Base):
    __tablename__ = "salary_components"

    component_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    structure_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)


class SalaryRevision(Base):
    __tablename__ = "salary_revisions"

    revision_id = Column(String, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("salary_components.component_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # High-precision Decimal for money
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)  # Null means currently active revision
    reason = Column(String, nullable=True)