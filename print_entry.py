from app.database import SessionLocal
from app.models.ledger import JournalEntry, JournalLine

def print_journal_entry(entry_id="JE-000007"):
    db = SessionLocal()
    try:
        # 1. Fetch the journal entry header
        entry = db.query(JournalEntry).filter_by(entry_id=entry_id).first()
        if not entry:
            print(f"Journal entry {entry_id} not found in database.")
            return

        # 2. Query the lines directly from the database by entry_id
        lines = db.query(JournalLine).filter_by(entry_id=entry_id).all()

        print("\n" + "=" * 70)
        print(f" JOURNAL ENTRY: {entry.entry_id}  |  DATE: {entry.date}")
        print(f" Description: {entry.description}")
        print("=" * 70)
        print(f" {'Line ID':<12} {'Account Code':<15} {'Debit (₹)':<15} {'Credit (₹)':<15}")
        print("-" * 70)

        total_debit = 0.0
        total_credit = 0.0

        for line in lines:
            line_id = getattr(line, 'line_id', getattr(line, 'id', 'N/A'))
            account_code = getattr(line, 'account_code', getattr(line, 'code', 'N/A'))
            debit_val = getattr(line, 'debit', 0.0) or 0.0
            credit_val = getattr(line, 'credit', 0.0) or 0.0
            
            total_debit += float(debit_val)
            total_credit += float(credit_val)
            
            print(f" {str(line_id):<12} {str(account_code):<15} {float(debit_val):<15.2f} {float(credit_val):<15.2f}")

        print("-" * 70)
        print(f" {'TOTALS':<27} {total_debit:<15.2f} {total_credit:<15.2f}")
        print("=" * 70)
        
        # Balancing Validation Check
        if round(total_debit, 2) == round(total_credit, 2):
            print(" Status: BALANCED [✓] (Debits match Credits)")
        else:
            print(" Status: UNBALANCED [✗] (Debits != Credits)")
        print("=" * 70 + "\n")

    finally:
        db.close()

if __name__ == "__main__":
    print_journal_entry("JE-000007")