from app.database import SessionLocal
from app.models.ledger import JournalLine, JournalEntry

db = SessionLocal()
try:
    ar_lines = db.query(JournalLine).filter_by(account_code="1100").all()
    print(f"Total lines for 1100: {len(ar_lines)}")
    
    tot_dr = sum(l.debit for l in ar_lines)
    tot_cr = sum(l.credit for l in ar_lines)
    print(f"Total Debits: ₹{tot_dr:,.2f}")
    print(f"Total Credits: ₹{tot_cr:,.2f}")
    print(f"Net: ₹{tot_dr - tot_cr:,.2f}")

    print("\nAll lines for account 1100:")
    for l in ar_lines:
        entry = db.query(JournalEntry).filter_by(entry_id=l.entry_id).first()
        desc = entry.description if entry else "N/A"
        print(f" - Entry: {l.entry_id} | Dr: {l.debit} | Cr: {l.credit} | Desc: {desc}")
finally:
    db.close()