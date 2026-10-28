from sqlalchemy import Column, String, Float, ForeignKey
from app.database import Base

class ChartOfAccounts(Base):
    __tablename__ = "chart_of_accounts"
    account_code = Column(String, primary_key=True, index=True)
    account_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    normal_balance = Column(String, nullable=False)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    entry_id = Column(String, primary_key=True, index=True)
    date = Column(String, nullable=False)
    description = Column(String, nullable=False)

class JournalLine(Base):
    __tablename__ = "journal_lines"
    line_id = Column(String, primary_key=True, index=True)
    entry_id = Column(String, ForeignKey("journal_entries.entry_id"), nullable=False)
    account_code = Column(String, ForeignKey("chart_of_accounts.account_code"), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)