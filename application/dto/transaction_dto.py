"""
Fuel Transaction Data Transfer Objects (DTOs) — Pydantic V2 compliant.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date
from decimal import Decimal
from typing import Optional, List

from application.dto.airline_dto import AirlineResponseDTO
from application.dto.vendor_dto import VendorResponseDTO


# ── Request DTOs ──────────────────────────────────────────────────────────────

class TransactionCreateDTO(BaseModel):
    airline_id: int = Field(..., json_schema_extra={"example": 1})
    vendor_id: int = Field(..., json_schema_extra={"example": 1})
    fuel_quantity: Decimal = Field(
        ..., gt=0, decimal_places=4,
        json_schema_extra={"example": 5000.0},
    )
    transaction_date: date = Field(
        ..., json_schema_extra={"example": "2024-06-22"},
    )
    remarks: Optional[str] = Field(
        None, max_length=1000,
        json_schema_extra={"example": "Regular refuelling"},
    )

    @field_validator("fuel_quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("fuel_quantity must be greater than zero")
        return v


# ── Response DTOs ─────────────────────────────────────────────────────────────

class TransactionResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_no: str
    airline_id: int
    vendor_id: int
    fuel_quantity: Decimal
    fuel_price: Decimal
    total_amount: Decimal
    transaction_date: date
    remarks: Optional[str] = None


class InvoiceResponseDTO(BaseModel):
    """Detailed invoice with nested airline/vendor information."""
    invoice_no: str
    transaction_date: date
    airline: AirlineResponseDTO
    vendor: VendorResponseDTO
    fuel_quantity_liters: float
    fuel_price_per_liter: float
    total_amount: float
    remarks: Optional[str] = None


class TransactionListResponseDTO(BaseModel):
    total: int
    data: List[TransactionResponseDTO]
