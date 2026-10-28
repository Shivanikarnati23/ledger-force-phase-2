from app.database import SessionLocal
from app.models.ledger import JournalEntry, JournalLine

db = SessionLocal()
try:
    entries = db.query(JournalEntry).all()
    print(f"Total Journal Entries in DB: {len(entries)}")
    
    non_inv_pay = []
    for entry in entries:
        if not entry.entry_id.startswith("JE-INV-") and not entry.entry_id.startswith("JE-PAY-"):
            non_inv_pay.append(entry)

    print(f"Entries that are NOT standard invoice/payment postings: {len(non_inv_pay)}")
    for e in non_inv_pay:
        lines = db.query(JournalLine).filter_by(entry_id=e.entry_id).all()
        print(f" - ID: {e.entry_id} | Date: {e.date} | Desc: {e.description}")
        for l in lines:
            print(f"     Line -> Acc: {l.account_code} | Dr: {l.debit} | Cr: {l.credit}")
finally:
    db.close()