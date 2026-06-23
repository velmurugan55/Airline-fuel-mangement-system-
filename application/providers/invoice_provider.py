"""
Invoice Provider — generates invoice numbers and structured invoice data.
Invoice Number Format: INV-YYYYMMDD-XXXX (4-digit sequence, zero-padded).
"""

from datetime import date
from sqlalchemy.orm import Session
from application.src.models.transaction_model import FuelTransaction
import logging

logger = logging.getLogger(__name__)


def generate_invoice_no(db: Session, transaction_date: date) -> str:
    """
    Generate a unique invoice number for the given date.
    Format: INV-YYYYMMDD-0001

    Counts existing invoices for the date and increments the sequence.
    """
    date_str = transaction_date.strftime("%Y%m%d")
    prefix = f"INV-{date_str}-"

    count = (
        db.query(FuelTransaction)
        .filter(FuelTransaction.invoice_no.like(f"{prefix}%"))
        .count()
    )
    sequence = count + 1
    invoice_no = f"{prefix}{sequence:04d}"
    logger.info("Generated invoice number: %s", invoice_no)
    return invoice_no


def build_invoice_data(transaction: FuelTransaction) -> dict:
    """
    Build a structured invoice dict from a transaction ORM object.
    Keys match AirlineResponseDTO and VendorResponseDTO field names exactly.
    """
    return {
        "invoice_no": transaction.invoice_no,
        "transaction_date": transaction.transaction_date,
        "airline": {
            "id": transaction.airline.id,
            "airline_code": transaction.airline.airline_code,
            "airline_name": transaction.airline.airline_name,
            "contact_person": transaction.airline.contact_person,
            "email": transaction.airline.email,
            "phone": transaction.airline.phone,
            "address": transaction.airline.address,
        },
        "vendor": {
            "id": transaction.vendor.id,
            "vendor_code": transaction.vendor.vendor_code,
            "vendor_name": transaction.vendor.vendor_name,
            "contact_person": transaction.vendor.contact_person,
            "email": transaction.vendor.email,
            "phone": transaction.vendor.phone,
            "address": transaction.vendor.address,
        },
        "fuel_quantity_liters": float(transaction.fuel_quantity),
        "fuel_price_per_liter": float(transaction.fuel_price),
        "total_amount": float(transaction.total_amount),
        "remarks": transaction.remarks or "",
    }
