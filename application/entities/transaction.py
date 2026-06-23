"""
Fuel Transaction Domain Entity.
"""

from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import Optional


class TransactionEntity(BaseModel):
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
