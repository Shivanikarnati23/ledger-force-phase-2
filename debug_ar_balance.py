from app.database import SessionLocal
from app.models.invoice import Invoice, InvoicePayment
from app.models.ledger import JournalLine

db = SessionLocal()
try:
    print("--- Checking first few invoices vs payments ---")
    invoices = db.query(Invoice).limit(3).all()
    for inv in invoices:
        inv_lines = db.query(JournalLine).filter_by(entry_id=f"JE-INV-{inv.invoice_id}").all()
        inv_dr = sum(l.debit for l in inv_lines if l.account_code == "1100")
        print(f"Invoice {inv.invoice_id}: Total = {inv.total} | AR Debited = {inv_dr}")

    payments = db.query(InvoicePayment).limit(3).all()
    for pay in payments:
        pay_lines = db.query(JournalLine).filter_by(entry_id=f"JE-PAY-{pay.payment_id}").all()
        pay_cr = sum(l.credit for l in pay_lines if l.account_code == "1100")
        print(f"Payment {pay.payment_id} (Invoice {pay.invoice_id}): Amount = {pay.amount} | AR Credited = {pay_cr}")
        
    total_inv_ar_dr = sum(l.debit for l in db.query(JournalLine).filter_by(account_code="1100").all() if l.debit > 0)
    total_pay_ar_cr = sum(l.credit for l in db.query(JournalLine).filter_by(account_code="1100").all() if l.credit > 0)
    print(f"\nTotal AR Debits (Invoices): {total_inv_ar_dr}")
    print(f"Total AR Credits (Payments): {total_pay_ar_cr}")
    print(f"Net AR Balance: {total_inv_ar_dr - total_pay_ar_cr}")
finally:
    db.close()