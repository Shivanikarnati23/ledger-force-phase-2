from app.database import SessionLocal
from app.models.ledger import JournalLine, JournalEntry

db = SessionLocal()
try:
    ar_lines = db.query(JournalLine).filter_by(account_code="1100").all()
    print(f"Total Journal Lines for 1100: {len(ar_lines)}")
    
    total_dr = sum(line.debit for line in ar_lines)
    total_cr = sum(line.credit for line in ar_lines)
    print(f"Total Debits: ₹{total_dr:,.2f}")
    print(f"Total Credits: ₹{total_cr:,.2f}")
    print(f"Net Balance: ₹{total_dr - total_cr:,.2f}")

    print("\nSample lines:")
    for line in ar_lines[:10]:
        entry = db.query(JournalEntry).filter_by(entry_id=line.entry_id).first()
        desc = entry.description if entry else "Unknown"
        print(f" - Entry {line.entry_id} | Dr: {line.debit} | Cr: {line.credit} | Desc: {desc}")
finally:
    db.close()