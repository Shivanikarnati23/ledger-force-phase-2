from app.database import SessionLocal
from app.services.ledger_service import create_journal_entry

db = SessionLocal()
try:
    # This should fail because Debits (500) != Credits (300)
    unbalanced_lines = [
        {"line_id": "L-TEST-1", "account_code": "1000", "debit": 500.0, "credit": 0.0},
        {"line_id": "L-TEST-2", "account_code": "2000", "debit": 0.0, "credit": 300.0}
    ]
    create_journal_entry(db, "JE-TEST-999", "2025-04-01", "Unbalanced Test", unbalanced_lines)
except ValueError as e:
    print(f"Validation Caught It: {e}")
finally:
    db.close()