from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
import csv
import os

app = FastAPI(title="Ledger Force Payroll & Payslip Engine")

def format_indian_currency(amount):
    """Formats numeric values into Indian numbering style (e.g., 1,23,456.00)."""
    try:
        val = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    
    s = f"{val:.2f}"
    parts = s.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]
    
    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 0:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        formatted_int = ",".join(groups) + "," + last_three if groups else last_three
        
    return f"{formatted_int}.{decimal_part}"


def verify_owner_or_hr(x_user_role: str = Header(default="")):
    """Security check: Only allow 'owner' or 'HR' roles via the X-User-Role header."""
    allowed_roles = ["owner", "hr", "Owner", "HR"]
    if x_user_role not in allowed_roles:
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Only the owner or HR may fetch a payslip."
        )
    return x_user_role


@app.get("/employees")
def list_employees(skip: int = 0, limit: int = 10, q: str | None = None, db: Session = Depends(get_db)):
    # Query database with optional search filter and pagination
    # Ensure returned Pydantic model excludes sensitive fields like date of birth
    pass


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    # Query single employee by ID
    employee = None # db.query(...).filter(...).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.get("/payslips/{employee_id}/{run_id}")
def get_payslip(employee_id: str, run_id: str, role: str = Depends(verify_owner_or_hr)):
    """Retrieves and formats a secure payslip for a given employee and run ID."""
    csv_file = "payroll_items.csv"
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="Reference payroll data file not found.")
    
    record = None
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("employee_id") == employee_id and row.get("run_id") == run_id:
                record = row
                break
    
    if not record:
        raise HTTPException(status_code=404, detail="Payslip record not found for the specified employee and run ID.")
    
    # Format all monetary figures using Indian currency formatting
    formatted_record = {
        "employee_id": record.get("employee_id"),
        "run_id": record.get("run_id"),
        "basic": format_indian_currency(record.get("basic", 0)),
        "allowances": format_indian_currency(record.get("allowances", 0)),
        "gross_pay": format_indian_currency(record.get("gross_pay", 0)),
        "deductions": format_indian_currency(record.get("deductions", 0)),
        "net_pay": format_indian_currency(record.get("net_pay", 0))
    }
    
    return {
        "status": "success",
        "authorized_role": role,
        "payslip": formatted_record
    }