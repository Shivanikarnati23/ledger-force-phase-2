import os
import pandas as pd
from sqlalchemy import Date, String, text
from app.database import engine, Base
import app.models  # Registers all models and constraints with Base.metadata

def normalize_emp_id(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.lower() in ['nan', 'none', '']:
        return None
    if s.replace('.', '', 1).isdigit():
        return f"EMP-{int(float(s)):04d}"
    s_upper = s.upper()
    if s_upper.startswith('EMP') and '-' not in s_upper:
        num_part = ''.join(filter(str.isdigit, s_upper))
        if num_part:
            return f"EMP-{int(num_part):04d}"
    if s_upper.startswith('E') and '-' not in s_upper and s_upper[1:].isdigit():
        return f"EMP-{int(s_upper[1:]):04d}"
    return s

def run_seeder():
    print("Starting data seeding from CSV files...")
    
    # Force drop and recreate the public schema cleanly to bypass foreign key locks
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))
    
    # Recreate tables fresh with all SQLAlchemy model constraints loaded
    Base.metadata.create_all(bind=engine)
    print("Database tables created fresh.")

    data_dir = "."

    # 1. Seed Departments
    dept_path = os.path.join(data_dir, "departments.csv")
    if os.path.exists(dept_path) and os.path.getsize(dept_path) > 0:
        df_dept = pd.read_csv(dept_path)
        for col in df_dept.select_dtypes(include=['object', 'str']).columns:
            df_dept[col] = df_dept[col].astype(str).str.strip()
        df_dept = df_dept.drop_duplicates()
        df_dept.to_sql('departments', con=engine, if_exists='append', index=False)
        print(f"Seeded departments: {len(df_dept)} rows.")

    # 2. Seed Roles
    roles_path = os.path.join(data_dir, "roles.csv")
    if os.path.exists(roles_path) and os.path.getsize(roles_path) > 0:
        df_roles = pd.read_csv(roles_path)
        for col in df_roles.select_dtypes(include=['object', 'str']).columns:
            df_roles[col] = df_roles[col].astype(str).str.strip()
        df_roles = df_roles.drop_duplicates()
        df_roles.to_sql('roles', con=engine, if_exists='append', index=False)
        print(f"Seeded roles: {len(df_roles)} rows.")

    # 3. Seed Employees
    emp_path = os.path.join(data_dir, "employees.csv")
    if os.path.exists(emp_path) and os.path.getsize(emp_path) > 0:
        df_emp = pd.read_csv(emp_path)
        if 'employee_id' in df_emp.columns:
            df_emp['employee_id'] = df_emp['employee_id'].apply(normalize_emp_id)
            df_emp = df_emp.drop_duplicates(subset=['employee_id'], keep='first').copy()
        
        for col in ['department_id', 'role_id', 'manager_id']:
            if col in df_emp.columns:
                df_emp[col] = df_emp[col].astype(str).str.strip().replace(['nan', 'None', ''], None)

        if 'exit_date' in df_emp.columns:
            df_emp['exit_date'] = pd.to_datetime(df_emp['exit_date'], errors='coerce').dt.date
        if 'hire_date' in df_emp.columns:
            df_emp['hire_date'] = pd.to_datetime(df_emp['hire_date'], errors='coerce').dt.date

        df_emp.to_sql(
            'employees', 
            con=engine, 
            if_exists='append', 
            index=False,
            dtype={
                'employee_id': String(),
                'first_name': String(),
                'last_name': String(),
                'email': String(),
                'department_id': String(),
                'role_id': String(),
                'manager_id': String(),
                'hire_date': Date(),
                'exit_date': Date(),
            }
        )
        print(f"Seeded employees: {len(df_emp)} rows.")

    # 4. Seed Employee Assignments
    assign_path = os.path.join(data_dir, "employee_assignments.csv")
    if os.path.exists(assign_path) and os.path.getsize(assign_path) > 0:
        df_assign = pd.read_csv(assign_path)
        for col in df_assign.select_dtypes(include=['object', 'str']).columns:
            df_assign[col] = df_assign[col].astype(str).str.strip()
        if 'employee_id' in df_assign.columns:
            df_assign['employee_id'] = df_assign['employee_id'].apply(normalize_emp_id)
        if 'assignment_id' in df_assign.columns:
            df_assign = df_assign.drop_duplicates(subset=['assignment_id'], keep='first')
        else:
            df_assign = df_assign.drop_duplicates()
        df_assign.to_sql('employee_assignments', con=engine, if_exists='append', index=False)
        print(f"Seeded employee_assignments: {len(df_assign)} rows.")

    # 5. Seed Salary Components
    comp_path = os.path.join(data_dir, "salary_components.csv")
    df_comp = pd.DataFrame()
    if os.path.exists(comp_path) and os.path.getsize(comp_path) > 0:
        df_comp = pd.read_csv(comp_path)
        for col in df_comp.select_dtypes(include=['object', 'str']).columns:
            df_comp[col] = df_comp[col].astype(str).str.strip()
            
        if 'component_name' in df_comp.columns and 'name' not in df_comp.columns:
            df_comp = df_comp.rename(columns={'component_name': 'name'})
        if 'component_type' in df_comp.columns and 'type' not in df_comp.columns:
            df_comp = df_comp.rename(columns={'component_type': 'type'})
            
        if 'component_id' in df_comp.columns:
            df_comp = df_comp.drop_duplicates(subset=['component_id'], keep='first')
            
    if df_comp.empty or 'COMP-BASIC' not in df_comp.get('component_id', pd.Series()).values:
        default_comp = pd.DataFrame([{'component_id': 'COMP-BASIC', 'name': 'Basic Salary', 'type': 'Earning', 'description': 'Standard Basic Salary'}])
        df_comp = pd.concat([df_comp, default_comp], ignore_index=True)

    valid_comp_cols = ['component_id', 'name', 'type', 'description']
    df_comp = df_comp[[c for c in valid_comp_cols if c in df_comp.columns]]

    df_comp.to_sql('salary_components', con=engine, if_exists='append', index=False)
    print(f"Seeded salary_components: {len(df_comp)} rows.")

    # 6. Seed Salary Revisions
    rev_path = os.path.join(data_dir, "salary_revisions.csv")
    if os.path.exists(rev_path) and os.path.getsize(rev_path) > 0:
        df_rev = pd.read_csv(rev_path)
        for col in df_rev.select_dtypes(include=['object', 'str']).columns:
            df_rev[col] = df_rev[col].astype(str).str.strip()
        
        if 'new_annual_fixed' in df_rev.columns:
            df_rev = df_rev.rename(columns={'new_annual_fixed': 'amount'})
        elif 'salary' in df_rev.columns:
            df_rev = df_rev.rename(columns={'salary': 'amount'})
            
        if 'effective_from' in df_rev.columns:
            df_rev = df_rev.rename(columns={'effective_from': 'valid_from'})
        elif 'effective_date' in df_rev.columns:
            df_rev = df_rev.rename(columns={'effective_date': 'valid_from'})
            
        if 'revision_reason' in df_rev.columns:
            df_rev = df_rev.rename(columns={'revision_reason': 'reason'})

        if 'component_id' not in df_rev.columns:
            df_rev['component_id'] = 'COMP-BASIC'

        if 'employee_id' in df_rev.columns:
            df_rev['employee_id'] = df_rev['employee_id'].apply(normalize_emp_id)

        if 'revision_id' in df_rev.columns:
            df_rev = df_rev.drop_duplicates(subset=['revision_id'], keep='first')
            
        if {'employee_id', 'component_id', 'valid_from'}.issubset(df_rev.columns):
            df_rev = df_rev.drop_duplicates(subset=['employee_id', 'component_id', 'valid_from'], keep='first')

        valid_rev_cols = ['revision_id', 'employee_id', 'component_id', 'amount', 'valid_from', 'valid_to', 'reason']
        df_rev = df_rev[[c for c in valid_rev_cols if c in df_rev.columns]]

        df_rev.to_sql('salary_revisions', con=engine, if_exists='append', index=False)
        print(f"Seeded salary_revisions: {len(df_rev)} rows.")
    else:
        print("Skipped salary_revisions.csv: file is empty.")

    # 7. Seed Salary Structures
    struct_path = os.path.join(data_dir, "salary_structures.csv")
    if os.path.exists(struct_path) and os.path.getsize(struct_path) > 0:
        df_struct = pd.read_csv(struct_path)
        for col in df_struct.select_dtypes(include=['object', 'str']).columns:
            df_struct[col] = df_struct[col].astype(str).str.strip()
            
        if 'monthly_amount' in df_struct.columns:
            df_struct = df_struct.rename(columns={'monthly_amount': 'base_salary'})
        elif 'amount' in df_struct.columns:
            df_struct = df_struct.rename(columns={'amount': 'base_salary'})

        if 'effective_from' in df_struct.columns:
            df_struct = df_struct.rename(columns={'effective_from': 'effective_date'})
        elif 'effective_date' not in df_struct.columns and 'date' in df_struct.columns:
            df_struct = df_struct.rename(columns={'date': 'effective_date'})
            
        if 'structure_id' in df_struct.columns:
            df_struct['structure_id'] = df_struct['structure_id'].apply(
                lambda x: f"SS-{int(float(x)):06d}" if str(x).replace('.', '', 1).isdigit() else str(x)
            )
        else:
            df_struct['structure_id'] = [f"SS-{i+1:06d}" for i in range(len(df_struct))]

        if 'employee_id' in df_struct.columns:
            df_struct['employee_id'] = df_struct['employee_id'].apply(normalize_emp_id)
            
        if 'component_id' in df_struct.columns:
            df_struct['component_id'] = df_struct['component_id'].apply(
                lambda x: 'COMP-BASIC' if str(x).isdigit() or str(x) in ['nan', 'None', ''] else str(x)
            )
        else:
            df_struct['component_id'] = 'COMP-BASIC'

        if 'effective_date' not in df_struct.columns:
            df_struct['effective_date'] = '2026-01-01'

        df_struct = df_struct.drop_duplicates(subset=['structure_id'], keep='first')

        if {'employee_id', 'component_id', 'effective_date'}.issubset(df_struct.columns):
            df_struct = df_struct.drop_duplicates(subset=['employee_id', 'component_id', 'effective_date'], keep='first')

        valid_struct_cols = ['structure_id', 'employee_id', 'component_id', 'base_salary', 'effective_date']
        df_struct = df_struct[[c for c in valid_struct_cols if c in df_struct.columns]]

        df_struct.to_sql('salary_structures', con=engine, if_exists='append', index=False)
        print(f"Seeded salary_structures: {len(df_struct)} rows.")
    else:
        print("Skipped salary_structures.csv: file is empty.")

    print("Database seeding completed successfully!")

    # Automatically print live database table counts
    print("\n--- Final Database Row Counts ---")
    with engine.connect() as conn:
        for table_name in ['departments', 'roles', 'employees', 'employee_assignments', 'salary_components', 'salary_revisions', 'salary_structures']:
            try:
                count = conn.execute(text(f"SELECT count(*) FROM {table_name};")).scalar()
                print(f"  - {table_name}: {count} rows")
            except Exception:
                pass
    print("---------------------------------\n")

if __name__ == "__main__":
    run_seeder()