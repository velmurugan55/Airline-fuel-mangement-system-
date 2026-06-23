"""
Airline Domain Entity (pure Pydantic model, decoupled from ORM).
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class AirlineEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    airline_code: str
    airline_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
