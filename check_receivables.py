from app.database import SessionLocal
from app.models.invoice import Client, Invoice, InvoicePayment
from app.models.ledger import JournalLine

def run_receivables_check():
    db = SessionLocal()
    try:
        print("==========================================")
        print("          RECEIVABLES LIST (WHO OWES WHAT)          ")
        print("==========================================")
        
        clients = db.query(Client).all()
        total_outstanding_all = 0.0

        for client in clients:
            client_invoices = db.query(Invoice).filter_by(client_id=client.client_id).all()
            client_total_due = 0.0
            
            print(f"\nClient: {client.name} (ID: {client.client_id})")
            
            for inv in client_invoices:
                payments = db.query(InvoicePayment).filter_by(invoice_id=inv.invoice_id).all()
                paid_amount = sum(p.amount for p in payments)
                
                balance_due = inv.total - paid_amount
                
                if inv.status in ["draft", "cancelled"]:
                    balance_due = 0.0

                if balance_due > 0.01:
                    print(f"  - Invoice {inv.invoice_id} | Status: {inv.status} | Total: ₹{inv.total:.2f} | Paid: ₹{paid_amount:.2f} | Due: ₹{balance_due:.2f}")
                    client_total_due += balance_due

            print(f"  --> Total Due from {client.name}: ₹{client_total_due:.2f}")
            total_outstanding_all += client_total_due

        print("\n==========================================")
        print(f"TOTAL OUTSTANDING RECEIVABLES (Open Invoices): ₹{total_outstanding_all:.2f}")
        print("==========================================")

        ar_lines = db.query(JournalLine).filter_by(account_code="1100").all()
        total_ar_debits = sum(line.debit for line in ar_lines)
        total_ar_credits = sum(line.credit for line in ar_lines)
        net_ledger_ar = total_ar_debits - total_ar_credits

        print("\n------------------------------------------")
        print("               CHECK 3 RESULTS              ")
        print("------------------------------------------")
        print(f"Ledger Accounts Receivable (1100) Net Balance: ₹{net_ledger_ar:.2f}")
        print(f"Sum of Open Invoices (Calculated Above):       ₹{total_outstanding_all:.2f}")

        difference = abs(net_ledger_ar - total_outstanding_all)
        if difference < 0.05:
            print("\nSTATUS: CHECK 3 PASSED [✓] (Ledger matches open invoices!)")
        else:
            print(f"\nSTATUS: CHECK 3 FAILED [X] (Discrepancy of ₹{difference:.2f})")

    except Exception as e:
        print(f"Error running receivables check: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_receivables_check()