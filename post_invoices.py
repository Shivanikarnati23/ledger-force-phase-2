from app.database import SessionLocal, engine, Base
from app.models.invoice import Invoice, InvoicePayment
from app.models.ledger import JournalEntry, JournalLine

def post_invoices_and_payments():
    # Ensure all tables (including ledger tables) exist in the database
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Process Invoices
        invoices = db.query(Invoice).all()
        for inv in invoices:
            # Rule: Draft and cancelled invoices must not post
            if inv.status in ["draft", "cancelled"]:
                print(f"Skipping invoice {inv.invoice_id} (Status: {inv.status}) - No ledger entry.")
                continue

            entry_id = f"JE-INV-{inv.invoice_id}"
            existing_entry = db.query(JournalEntry).filter_by(entry_id=entry_id).first()
            
            if existing_entry:
                print(f"Journal entry for invoice {inv.invoice_id} already exists.")
                continue

            # Create Journal Entry for the Invoice
            desc = f"Invoice {inv.invoice_id} - Client {inv.client_id}"
            journal_entry = JournalEntry(
                entry_id=entry_id,
                date=inv.date,
                description=desc
            )
            db.add(journal_entry)
            db.flush()

            # Rule: Invoice debits receivables (1100) and credits income/tax
            ar_line = JournalLine(
                line_id=f"JL-{entry_id}-1",
                entry_id=entry_id,
                account_code="1100",
                debit=inv.total,
                credit=0.0
            )
            db.add(ar_line)

            if inv.subtotal > 0:
                income_line = JournalLine(
                    line_id=f"JL-{entry_id}-2",
                    entry_id=entry_id,
                    account_code="4004",  # Income account code
                    debit=0.0,
                    credit=inv.subtotal
                )
                db.add(income_line)

            if inv.tax_total > 0:
                tax_line = JournalLine(
                    line_id=f"JL-{entry_id}-3",
                    entry_id=entry_id,
                    account_code="2200",  # Tax liability code
                    debit=0.0,
                    credit=inv.tax_total
                )
                db.add(tax_line)

            print(f"Posted invoice {inv.invoice_id} to ledger.")

        # 2. Process Payments
        payments = db.query(InvoicePayment).all()
        for pay in payments:
            pay_entry_id = f"JE-PAY-{pay.payment_id}"
            existing_pay_entry = db.query(JournalEntry).filter_by(entry_id=pay_entry_id).first()

            if existing_pay_entry:
                continue

            pay_entry = JournalEntry(
                entry_id=pay_entry_id,
                date=pay.date,
                description=f"Payment {pay.payment_id} for Invoice {pay.invoice_id}"
            )
            db.add(pay_entry)
            db.flush()

            bank_line = JournalLine(
                line_id=f"JL-{pay_entry_id}-1",
                entry_id=pay_entry_id,
                account_code="1000",  # Bank account code
                debit=pay.amount,
                credit=0.0
            )
            db.add(bank_line)

            ar_credit_line = JournalLine(
                line_id=f"JL-{pay_entry_id}-2",
                entry_id=pay_entry_id,
                account_code="1100",
                debit=0.0,
                credit=pay.amount
            )
            db.add(ar_credit_line)

            print(f"Posted payment {pay.payment_id} to ledger.")

        db.commit()
        print("Successfully processed all invoice and payment postings!")

    except Exception as e:
        db.rollback()
        print(f"Error posting records: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    post_invoices_and_payments()