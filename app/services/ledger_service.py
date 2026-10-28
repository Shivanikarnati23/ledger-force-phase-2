from sqlalchemy.orm import Session
from app.models.ledger import JournalEntry, JournalLine

def create_journal_entry(db: Session, entry_id: str, date: str, description: str, lines: list[dict]):
    """
    Creates a journal entry after validating that total debits equal total credits.
    
    Each item in 'lines' should look like:
    {"account_code": "1000", "debit": 500.0, "credit": 0.0}
    """
    total_debits = sum(line.get("debit", 0.0) for line in lines)
    total_credits = sum(line.get("credit", 0.0) for line in lines)

    # Use round to handle minor floating-point representation differences
    if round(total_debits, 2) != round(total_credits, 2):
        raise ValueError(
            f"Journal entry {entry_id} is unbalanced! "
            f"Total Debits ({total_debits}) must equal Total Credits ({total_credits})."
        )

    # Create the Journal Entry header
    db_entry = JournalEntry(entry_id=entry_id, date=date, description=description)
    db.add(db_entry)

    # Create the Journal Lines
    for line in lines:
        db_line = JournalLine(
            line_id=line.get("line_id"),
            entry_id=entry_id,
            account_code=line.get("account_code"),
            debit=line.get("debit", 0.0),
            credit=line.get("credit", 0.0)
        )
        db.add(db_line)

    db.commit()
    print(f"Successfully created balanced journal entry: {entry_id}")
    return db_entry