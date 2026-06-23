"""
Airline Data Transfer Objects (DTOs) — Pydantic V2 compliant.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# ── Request DTOs ──────────────────────────────────────────────────────────────

class AirlineCreateDTO(BaseModel):
    airline_code: str = Field(
        ..., min_length=2, max_length=20,
        json_schema_extra={"example": "GA"},
    )
    airline_name: str = Field(
        ..., min_length=2, max_length=200,
        json_schema_extra={"example": "Garuda Indonesia"},
    )
    contact_person: Optional[str] = Field(
        None, max_length=150,
        json_schema_extra={"example": "John Doe"},
    )
    email: Optional[str] = Field(
        None, max_length=254,
        json_schema_extra={"example": "ops@garuda.com"},
    )
    phone: Optional[str] = Field(
        None, max_length=30,
        json_schema_extra={"example": "+62-21-2351-9999"},
    )
    address: Optional[str] = Field(
        None, max_length=500,
        json_schema_extra={"example": "Soekarno-Hatta Airport, Tangerang"},
    )


class AirlineUpdateDTO(BaseModel):
    airline_name: Optional[str] = Field(None, min_length=2, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=150)
    email: Optional[str] = Field(None, max_length=254)
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = Field(None, max_length=500)


# ── Response DTOs ─────────────────────────────────────────────────────────────

class AirlineResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    airline_code: str
    airline_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class AirlineListResponseDTO(BaseModel):
    total: int
    data: List[AirlineResponseDTO]
