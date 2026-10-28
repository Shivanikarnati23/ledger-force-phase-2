import os
import csv
from app.database import SessionLocal, engine, Base
from app.models.invoice import Invoice

def load_invoices_data():
    Base.metadata.create_all(bind=engine)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "invoices.csv")
    
    if not os.path.exists(csv_path):
        print(f"ERROR: Could not find 'invoices.csv' at {csv_path}")
        return

    db = SessionLocal()
    try:
        print(f"Loading invoices from {csv_path}...")
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                clean_row = {str(k).lower().strip(): v for k, v in row.items() if k is not None}
                
                invoice_id = clean_row.get("invoice_id")
                if not invoice_id:
                    continue

                def clean_float(val):
                    if not val:
                        return 0.0
                    try:
                        return float(str(val).replace(",", "").strip())
                    except ValueError:
                        return 0.0

                subtotal = clean_float(clean_row.get("subtotal"))
                tax_total = clean_float(clean_row.get("gst_amount"))
                total = clean_float(clean_row.get("total_amount"))
                
                # Capture date and due_date checking multiple possible CSV column name variations
                invoice_date = (
                    clean_row.get("invoice_date") or 
                    clean_row.get("date") or 
                    clean_row.get("invoice_dt") or 
                    "2026-01-01"
                )
                due_date = (
                    clean_row.get("due_date") or 
                    clean_row.get("duedate") or 
                    invoice_date
                )
                
                existing = db.query(Invoice).filter_by(invoice_id=invoice_id).first()
                if not existing:
                    invoice = Invoice(
                        invoice_id=invoice_id,
                        client_id=clean_row.get("client_id"),
                        date=invoice_date,
                        due_date=due_date,
                        subtotal=subtotal,
                        tax_total=tax_total,
                        total=total,
                        status=clean_row.get("status", "").lower() or "paid"
                    )
                    db.add(invoice)
                    count += 1

            db.commit()
            print(f"Successfully loaded {count} invoice records!")

    except Exception as e:
        db.rollback()
        print(f"Error loading invoices: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    load_invoices_data()