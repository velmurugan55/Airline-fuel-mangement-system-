"""
Fuel Vendor Data Transfer Objects (DTOs) — Pydantic V2 compliant.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# ── Request DTOs ──────────────────────────────────────────────────────────────

class VendorCreateDTO(BaseModel):
    vendor_code: str = Field(
        ..., min_length=2, max_length=20,
        json_schema_extra={"example": "PT-FUEL"},
    )
    vendor_name: str = Field(
        ..., min_length=2, max_length=200,
        json_schema_extra={"example": "PT Pertamina Fuel"},
    )
    contact_person: Optional[str] = Field(
        None, max_length=150,
        json_schema_extra={"example": "Jane Smith"},
    )
    email: Optional[str] = Field(
        None, max_length=254,
        json_schema_extra={"example": "contact@pertamina.com"},
    )
    phone: Optional[str] = Field(
        None, max_length=30,
        json_schema_extra={"example": "+62-21-1234-5678"},
    )
    address: Optional[str] = Field(
        None, max_length=500,
        json_schema_extra={"example": "Jakarta Pusat, DKI Jakarta"},
    )
    gst_number: Optional[str] = Field(
        None, max_length=50,
        json_schema_extra={"example": "27AABCU9603R1ZM"},
    )


class VendorUpdateDTO(BaseModel):
    vendor_name: Optional[str] = Field(None, min_length=2, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=150)
    email: Optional[str] = Field(None, max_length=254)
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = Field(None, max_length=500)
    gst_number: Optional[str] = Field(None, max_length=50)


# ── Response DTOs ─────────────────────────────────────────────────────────────

class VendorResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_code: str
    vendor_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None


class VendorListResponseDTO(BaseModel):
    total: int
    data: List[VendorResponseDTO]
