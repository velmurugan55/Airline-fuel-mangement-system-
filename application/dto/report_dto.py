"""
Report Data Transfer Objects (DTOs) — Pydantic V2 compliant.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from decimal import Decimal
from typing import Optional, List


# ── Query Filters ─────────────────────────────────────────────────────────────

class ReportFilterDTO(BaseModel):
    from_date: Optional[date] = Field(None, json_schema_extra={"example": "2024-01-01"})
    to_date: Optional[date] = Field(None, json_schema_extra={"example": "2024-12-31"})
    airline_id: Optional[int] = Field(None, json_schema_extra={"example": 1})
    vendor_id: Optional[int] = Field(None, json_schema_extra={"example": 1})


# ── Invoice Report ────────────────────────────────────────────────────────────

class InvoiceReportItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invoice_no: str
    transaction_date: date
    airline_name: str
    airline_code: str
    vendor_name: str
    vendor_code: str
    fuel_quantity: Decimal
    fuel_price: Decimal
    total_amount: Decimal
    remarks: Optional[str] = None


class InvoiceReportResponseDTO(BaseModel):
    total_records: int
    total_fuel_quantity: Decimal
    total_amount: Decimal
    invoices: List[InvoiceReportItemDTO]


# ── Dashboard Report ──────────────────────────────────────────────────────────

class TopAirlineDTO(BaseModel):
    airline_id: int
    airline_name: str
    total_fuel: Decimal
    total_amount: Decimal


class TopVendorDTO(BaseModel):
    vendor_id: int
    vendor_name: str
    total_fuel: Decimal
    total_amount: Decimal


class DashboardResponseDTO(BaseModel):
    period_from: Optional[date]
    period_to: Optional[date]
    total_transactions: int
    total_fuel_quantity: Decimal
    total_revenue: Decimal
    top_airlines: List[TopAirlineDTO]
    top_vendors: List[TopVendorDTO]
