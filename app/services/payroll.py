from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel
import csv
import os
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.database import get_db
from app.models.salary import SalaryStructure, SalaryRevision, SalaryComponent

router = APIRouter(prefix="/payroll", tags=["Salary & Compensation"])

class SalaryStructureResponse(BaseModel):
    structure_id: str
    employee_id: str
    component_id: Optional[str] = None
    base_salary: Decimal
    effective_date: date

    class Config:
        from_attributes = True

class SalaryRevisionResponse(BaseModel):
    revision_id: str
    employee_id: str
    component_id: str
    amount: Decimal
    valid_from: date
    valid_to: Optional[date] = None
    reason: Optional[str] = None  # Tracks the reason for each revision change

    class Config:
        from_attributes = True


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


@router.get("/structure/{employee_id}", response_model=SalaryStructureResponse)
def get_employee_salary_structure(
    employee_id: str, 
    as_of_date: Optional[date] = Query(None, description="Target date for effective dating lookup"),
    db: Session = Depends(get_db)
):
    target_date = as_of_date or date.today()
    
    query = select(SalaryStructure).where(
        and_(
            SalaryStructure.employee_id == employee_id,
            SalaryStructure.effective_date <= target_date
        )
    ).order_by(SalaryStructure.effective_date.desc())
    
    structure = db.execute(query).scalars().first()
    if not structure:
        raise HTTPException(status_code=404, detail="Salary structure not found for this employee on the given date.")
    
    return structure


@router.get("/revisions/{employee_id}", response_model=List[SalaryRevisionResponse])
def get_employee_salary_revisions(employee_id: str, db: Session = Depends(get_db)):
    query = select(SalaryRevision).where(SalaryRevision.employee_id == employee_id).order_by(SalaryRevision.valid_from.desc())
    revisions = db.execute(query).scalars().all()
    
    if not revisions:
        raise HTTPException(status_code=404, detail="No salary revision history found for this employee.")
        
    return revisions


@router.get("/payslips/{employee_id}/{run_id}/pdf")
def get_payslip_pdf(employee_id: str, run_id: str, role: str = Depends(verify_owner_or_hr)):
    """Generates and returns an official PDF payslip using ReportLab with Net Pay prominent."""
    csv_file = "payroll_items.csv"
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="Reference payroll items data file not found.")
    
    record = None
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("employee_id") == employee_id and row.get("run_id") == run_id:
                record = row
                break
                
    if not record:
        raise HTTPException(status_code=404, detail="Payslip record not found for the given employee and run ID.")
    
    # Format amounts the Indian way
    basic_fmt = format_indian_currency(record.get("basic", 0))
    allowances_fmt = format_indian_currency(record.get("allowances", 0))
    gross_fmt = format_indian_currency(record.get("gross_pay", 0))
    deductions_fmt = format_indian_currency(record.get("deductions", 0))
    net_fmt = format_indian_currency(record.get("net_pay", 0))
    
    # Generate PDF into memory buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#004080'), alignment=1)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#666666'), alignment=1)
    cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#333333'))
    bold_cell = ParagraphStyle('BoldCell', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#333333'))
    
    story.append(Paragraph("Ledger Force Pvt. Ltd.", title_style))
    story.append(Paragraph("Official Salary Payslip", sub_style))
    story.append(Spacer(1, 15))
    
    # Metadata Table
    meta_data = [
        [Paragraph(f"<b>Employee ID:</b> {record.get('employee_id')}", cell_style),
         Paragraph(f"<b>Run ID:</b> {record.get('run_id')}", cell_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Earnings & Deductions Table
    table_data = [
        [Paragraph("<b>Earnings & Deductions Description</b>", cell_style), Paragraph("<b>Amount (INR)</b>", cell_style)],
        [Paragraph("Basic Salary", cell_style), Paragraph(basic_fmt, cell_style)],
        [Paragraph("Allowances", cell_style), Paragraph(allowances_fmt, cell_style)],
        [Paragraph("<b>Gross Pay</b>", bold_cell), Paragraph(f"<b>{gross_fmt}</b>", bold_cell)],
        [Paragraph("Total Deductions", cell_style), Paragraph(deductions_fmt, cell_style)]
    ]
    t = Table(table_data, colWidths=[330, 170])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Prominent Net Pay Box
    net_data = [[
        Paragraph(f"<font size=12 color='#004080'><b>NET PAY (TAKE-HOME SALARY)</b></font><br/><br/>"
                  f"<font size=24 color='#003366'><b>Rs. {net_fmt}</b></font>", 
                  ParagraphStyle('NetStyle', alignment=1))
    ]]
    net_table = Table(net_data, colWidths=[500])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f2ff')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#004080')),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(net_table)
    
    doc.build(story)
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(), 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=payslip_{employee_id}_{run_id}.pdf"}
    )