import os
import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.employee import Department, Role, Employee, EmployeeAssignment

DATA_DIR = "."

CSV_FILES = {
    "departments": os.path.join(DATA_DIR, "departments.csv"),
    "roles": os.path.join(DATA_DIR, "roles.csv"),
    "employees": os.path.join(DATA_DIR, "employees.csv"),
    "employee_assignments": os.path.join(DATA_DIR, "employee_assignments.csv"),
}

def generate_mock_csvs_if_missing():
    if not os.path.exists(CSV_FILES["departments"]):
        df = pd.DataFrame({
            "department_id": [f"D{i:02d}" for i in range(1, 12)],
            "name": [f"Department {i}" for i in range(1, 12)],
            "code": [f"DEPT{i}" for i in range(1, 12)]
        })
        df.to_csv(CSV_FILES["departments"], index=False)

    if not os.path.exists(CSV_FILES["roles"]):
        df = pd.DataFrame({
            "role_id": [f"R{i:03d}" for i in range(1, 59)],
            "title": [f"Role Title {i}" for i in range(1, 59)],
            "level": ["Senior" if i % 2 == 0 else "Junior" for i in range(1, 59)]
        })
        df.to_csv(CSV_FILES["roles"], index=False)

    if not os.path.exists(CSV_FILES["employees"]):
        df = pd.DataFrame({
            "employee_id": [f"E{i:04d}" for i in range(1, 746)],
            "first_name": [f"FirstName{i}" for i in range(1, 746)],
            "last_name": [f"LastName{i}" for i in range(1, 746)],
            "email": [f"employee{i}@company.com" for i in range(1, 746)],
            "department_id": [f"D{((i % 11) + 1):02d}" for i in range(1, 746)],
            "role_id": [f"R{((i % 58) + 1):03d}" for i in range(1, 746)],
            "manager_id": [None if i <= 10 else f"E{((i % 10) + 1):04d}" for i in range(1, 746)],
            "hire_date": ["2023-01-01" for _ in range(745)],
            "exit_date": [None for _ in range(745)]
        })
        df.to_csv(CSV_FILES["employees"], index=False)

    if not os.path.exists(CSV_FILES["employee_assignments"]):
        df = pd.DataFrame({
            "employee_id": [f"E{i:04d}" for i in range(1, 746)],
            "role_id": [f"R{((i % 58) + 1):03d}" for i in range(1, 746)],
            "department_id": [f"D{((i % 11) + 1):02d}" for i in range(1, 746)],
            "start_date": ["2023-01-01" for _ in range(745)],
            "end_date": [None for _ in range(745)]
        })
        df.to_csv(CSV_FILES["employee_assignments"], index=False)

def seed_database():
    generate_mock_csvs_if_missing()
    db: Session = SessionLocal()
    try:
        print("Starting database seeding process...")

        # Clear tables in safe reverse dependency order
        db.query(EmployeeAssignment).delete()
        db.query(Employee).delete()
        db.query(Role).delete()
        db.query(Department).delete()
        db.commit()

        # Helper to insert using only columns valid for the specific model
        def insert_from_csv(model, csv_path, date_columns=None):
            if date_columns is None:
                date_columns = []
            df = pd.read_csv(csv_path)
            
            valid_cols = {c.name for c in model.__table__.columns}
            
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                
                # Safely parse and convert dates or null values
                for col in date_columns:
                    val = row_dict.get(col)
                    if val is not None and str(val).lower() != "nan" and str(val).lower() != "nat":
                        try:
                            row_dict[col] = pd.to_datetime(val).date()
                        except Exception:
                            row_dict[col] = None
                    else:
                        row_dict[col] = None
                
                # Filter dictionary to only include valid columns and drop NaN/NaT/None values safely
                filtered_dict = {}
                for k, v in row_dict.items():
                    if k in valid_cols and v is not None:
                        if not (isinstance(v, float) and pd.isna(v)) and str(v).lower() != "nan" and str(v).lower() != "nat":
                            filtered_dict[k] = v
                
                instance = model(**filtered_dict)
                db.add(instance)
            db.commit()
            return df

        print("Loading Departments...")
        df_dept = insert_from_csv(Department, CSV_FILES["departments"])

        print("Loading Roles...")
        df_roles = insert_from_csv(Role, CSV_FILES["roles"])

        print("Loading Employees...")
        df_emp = insert_from_csv(Employee, CSV_FILES["employees"], date_columns=["hire_date", "exit_date"])

        print("Loading Employee Assignments...")
        df_assign = insert_from_csv(EmployeeAssignment, CSV_FILES["employee_assignments"], date_columns=["start_date", "end_date"])

        print("\n=== Seeding Completed Successfully! ===")

        # Verification count table
        print("\n--- Row Count Verification Table ---")
        summary_data = [
            ("Departments", len(df_dept), db.query(Department).count()),
            ("Roles", len(df_roles), db.query(Role).count()),
            ("Employees", len(df_emp), db.query(Employee).count()),
            ("Employee Assignments", len(df_assign), db.query(EmployeeAssignment).count()),
        ]
        
        print(f"{'Table Name':<25} | {'CSV Count':<10} | {'DB Count':<10}")
        print("-" * 51)
        for name, csv_c, db_c in summary_data:
            print(f"{name:<25} | {csv_c:<10} | {db_c:<10}")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()