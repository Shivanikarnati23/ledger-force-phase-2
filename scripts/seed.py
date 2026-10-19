import csv
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from app.database import SessionLocal
from app.models.salary import SalaryComponent, SalaryStructure, SalaryRevision

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

def seed_salary_data():
    db = SessionLocal()
    try:
        # 1. Seed Salary Components
        with open(BASE_DIR / "salary_components.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                component = db.query(SalaryComponent).filter_by(component_id=row["component_id"]).first()
                if not component:
                    component = SalaryComponent(
                        component_id=row["component_id"],
                        name=row["name"],
                        description=row.get("description")
                    )
                    db.add(component)
        
        # 2. Seed Salary Structures
        with open(BASE_DIR / "salary_structures.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                structure = db.query(SalaryStructure).filter_by(structure_id=row["structure_id"]).first()
                if not structure:
                    structure = SalaryStructure(
                        structure_id=row["structure_id"],
                        name=row["name"]
                    )
                    db.add(structure)

        # 3. Seed Salary Revisions
        with open(BASE_DIR / "salary_revisions.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                revision = db.query(SalaryRevision).filter_by(revision_id=row["revision_id"]).first()
                if not revision:
                    revision = SalaryRevision(
                        revision_id=row["revision_id"],
                        employee_id=row["employee_id"],
                        component_id=row["component_id"],
                        amount=Decimal(row["amount"]),
                        valid_from=datetime.strptime(row["valid_from"], "%Y-%m-%d").date(),
                        valid_to=datetime.strptime(row["valid_to"], "%Y-%m-%d").date() if row.get("valid_to") else None,
                        reason=row.get("reason")
                    )
                    db.add(revision)

        db.commit()
        print("Salary data seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding salary data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_salary_data()