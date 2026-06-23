"""
Fuel Price Data Transfer Objects (DTOs) — Pydantic V2 compliant.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date
from decimal import Decimal
from typing import List


# ── Request DTOs ──────────────────────────────────────────────────────────────

class FuelPriceCreateDTO(BaseModel):
    vendor_id: int = Field(..., json_schema_extra={"example": 1})
    price_per_liter: Decimal = Field(
        ..., gt=0, decimal_places=4,
        json_schema_extra={"example": 12345.5},
    )
    effective_date: date = Field(
        ..., json_schema_extra={"example": "2024-06-01"},
    )

    @field_validator("price_per_liter")
    @classmethod
    def price_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("price_per_liter must be greater than zero")
        return v


class FuelPriceUpdateDTO(BaseModel):
    price_per_liter: Decimal = Field(
        ..., gt=0, decimal_places=4,
        json_schema_extra={"example": 13000.0},
    )
    effective_date: date = Field(
        ..., json_schema_extra={"example": "2024-07-01"},
    )


# ── Response DTOs ─────────────────────────────────────────────────────────────

class FuelPriceResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int
    price_per_liter: Decimal
    effective_date: date


class FuelPriceListResponseDTO(BaseModel):
    vendor_id: int
    history: List[FuelPriceResponseDTO]
