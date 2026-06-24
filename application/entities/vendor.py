"""
Fuel Vendor Domain Entity.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class VendorEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_code: str
    vendor_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
