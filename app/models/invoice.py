from sqlalchemy import Column, String, Float, Date, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    part_paid = "part-paid"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"

class Client(Base):
    __tablename__ = "clients"

    client_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)

    # Relationship to invoices
    invoices = relationship("Invoice", back_populates="client")

class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default=InvoiceStatus.draft, nullable=False)
    subtotal = Column(Float, nullable=False, default=0.0)
    tax_total = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)

    # Relationships
    client = relationship("Client", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("InvoicePayment", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    item_id = Column(String, primary_key=True, index=True)
    invoice_id = Column(String, ForeignKey("invoices.invoice_id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    unit_price = Column(Float, nullable=False, default=0.0)
    amount = Column(Float, nullable=False, default=0.0)
    tax_rate = Column(Float, nullable=False, default=0.0)

    # Relationship
    invoice = relationship("Invoice", back_populates="items")

class InvoicePayment(Base):
    __tablename__ = "invoice_payments"

    payment_id = Column(String, primary_key=True, index=True)
    invoice_id = Column(String, ForeignKey("invoices.invoice_id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String, nullable=True)

    # Relationship
    invoice = relationship("Invoice", back_populates="payments")