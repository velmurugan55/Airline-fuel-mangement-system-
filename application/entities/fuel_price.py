"""
Fuel Price Domain Entity.
"""

from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal


class FuelPriceEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int
    price_per_liter: Decimal
    effective_date: date
