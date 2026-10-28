import csv
import os
from app.database import Base, engine, SessionLocal
from app.models.ledger import ChartOfAccounts, JournalEntry, JournalLine

def load_csv_data():
    # Automatically create missing database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables verified/created successfully!")

    db = SessionLocal()
    
    try:
        # 1. Load Chart of Accounts
        coa_file = "chart_of_accounts.csv"
        if os.path.exists(coa_file):
            with open(coa_file, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for raw_row in reader:
                    # Clean/normalize column names to lowercase and strip whitespace
                    row = {k.strip().lower(): v for k, v in raw_row.items() if k}
                    account_code = row.get("account_code")
                    if not account_code:
                        continue
                    exists = db.query(ChartOfAccounts).filter_by(account_code=account_code).first()
                    if not exists:
                        account = ChartOfAccounts(
                            account_code=account_code,
                            account_name=row.get("account_name"),
                            account_type=row.get("account_type"),
                            normal_balance=row.get("normal_balance")
                        )
                        db.add(account)
            db.commit()
            print("Successfully loaded Chart of Accounts!")

        # 2. Load Journal Entries
        je_file = "journal_entries.csv"
        if os.path.exists(je_file):
            with open(je_file, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for raw_row in reader:
                    row = {k.strip().lower(): v for k, v in raw_row.items() if k}
                    entry_id = row.get("entry_id")
                    if not entry_id:
                        continue
                    exists = db.query(JournalEntry).filter_by(entry_id=entry_id).first()
                    if not exists:
                        # Find date and description dynamically regardless of exact casing
                        entry_date = next((v for k, v in row.items() if 'date' in k), None)
                        entry_desc = next((v for k, v in row.items() if 'desc' in k), "")
                        
                        entry = JournalEntry(
                            entry_id=entry_id,
                            date=entry_date,
                            description=entry_desc
                        )
                        db.add(entry)
            db.commit()
            print("Successfully loaded Journal Entries!")

        # 3. Load Journal Lines
        jl_file = "journal_lines.csv"
        if os.path.exists(jl_file):
            with open(jl_file, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for raw_row in reader:
                    row = {k.strip().lower(): v for k, v in raw_row.items() if k}
                    line_id = row.get("line_id")
                    if not line_id:
                        continue
                    exists = db.query(JournalLine).filter_by(line_id=line_id).first()
                    if not exists:
                        debit_val, credit_val = 0.0, 0.0
                        for k, v in row.items():
                            if 'debit' in k and v:
                                try: debit_val = float(v)
                                except ValueError: pass
                            elif 'credit' in k and v:
                                try: credit_val = float(v)
                                except ValueError: pass

                        line = JournalLine(
                            line_id=line_id,
                            entry_id=row.get("entry_id"),
                            account_code=row.get("account_code"),
                            debit=debit_val,
                            credit=credit_val
                        )
                        db.add(line)
            db.commit()
            print("Successfully loaded Journal Lines!")

    except Exception as e:
        db.rollback()
        print(f"Error loading CSV data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    load_csv_data()