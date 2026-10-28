from sqlalchemy import Column, String, Numeric, Date, ForeignKey, UniqueConstraint
from app.database import Base

class SalaryComponent(Base):
    __tablename__ = "salary_components"

    component_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)  # Earning, Deduction, etc.
    description = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint('component_id', name='uq_salary_components_component_id'),
    )


class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    structure_id = Column(String, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("salary_components.component_id", ondelete="CASCADE"), nullable=True, index=True)
    base_salary = Column(Numeric(12, 2), nullable=False)  # Maps to Decimal
    effective_date = Column(Date, nullable=False)

    __table_args__ = (
       UniqueConstraint('employee_id', 'component_id', 'effective_date', name='uq_salary_structures_emp_comp_effective'),
    )


class SalaryRevision(Base):
    __tablename__ = "salary_revisions"

    revision_id = Column(String, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("salary_components.component_id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)  # Maps to Decimal
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)
    reason = Column(String, nullable=True)  # Tracks the reason for each revision change

    __table_args__ = (
        UniqueConstraint('employee_id', 'component_id', 'valid_from', name='uq_salary_revisions_emp_comp_from'),
    )