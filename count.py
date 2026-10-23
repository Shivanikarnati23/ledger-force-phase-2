from app.database import SessionLocal
from sqlalchemy import text

s = SessionLocal()
try:
    tables = s.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name != 'alembic_version'")).fetchall()
    print("--- Database Table Row Counts ---")
    for t in tables:
        count = s.execute(text(f"SELECT COUNT(*) FROM {t[0]}")).scalar()
        print(f"{t[0]}: {count}")
finally:
    s.close()