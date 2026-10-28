import csv
from app.database import SessionLocal, engine, Base
from sqlalchemy import text

def load_chart_of_accounts():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Loading chart of accounts...")
        with open("chart_of_accounts.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                code = row.get("account_code") or row.get("code")
                name = row.get("account_name") or row.get("name")
                atype = row.get("account_type") or row.get("type")
                
                # Determine normal balance if not explicitly in CSV (Assets/Expenses are Debit, Liabilities/Equity/Revenue are Credit)
                normal_bal = row.get("normal_balance")
                if not normal_bal:
                    normal_bal = "DEBIT" if atype and atype.upper() in ["ASSET", "EXPENSE"] else "CREDIT"

                # Check if exists
                exists = db.execute(
                    text("SELECT 1 FROM chart_of_accounts WHERE account_code = :code"),
                    {"code": code}
                ).fetchone()

                if not exists:
                    db.execute(
                        text("INSERT INTO chart_of_accounts (account_code, account_name, account_type, normal_balance) VALUES (:code, :name, :atype, :nbal)"),
                        {"code": code, "name": name, "atype": atype, "nbal": normal_bal}
                    )
                    count += 1

            db.commit()
            print(f"Successfully loaded {count} chart of accounts entries!")

    except Exception as e:
        db.rollback()
        print(f"Error loading chart of accounts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    load_chart_of_accounts()