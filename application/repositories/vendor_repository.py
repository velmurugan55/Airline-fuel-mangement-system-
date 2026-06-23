"""
Fuel Vendor Repository — DB operations for the FuelVendor model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from application.src.models.vendor_model import FuelVendor
from application.dto.vendor_dto import VendorCreateDTO, VendorUpdateDTO
import logging

logger = logging.getLogger(__name__)


class VendorRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vendor_id: int) -> Optional[FuelVendor]:
        return self.db.query(FuelVendor).filter(FuelVendor.id == vendor_id).first()

    def get_by_code(self, vendor_code: str) -> Optional[FuelVendor]:
        return self.db.query(FuelVendor).filter(FuelVendor.vendor_code == vendor_code).first()

    def get_all(self) -> List[FuelVendor]:
        return self.db.query(FuelVendor).order_by(FuelVendor.vendor_name).all()

    def create(self, dto: VendorCreateDTO) -> FuelVendor:
        vendor = FuelVendor(**dto.model_dump())
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        logger.info("Created vendor: %s (%s)", vendor.vendor_name, vendor.vendor_code)
        return vendor

    def update(self, vendor: FuelVendor, dto: VendorUpdateDTO) -> FuelVendor:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)
        self.db.commit()
        self.db.refresh(vendor)
        logger.info("Updated vendor id=%s", vendor.id)
        return vendor

    def delete(self, vendor: FuelVendor) -> None:
        self.db.delete(vendor)
        self.db.commit()
        logger.info("Deleted vendor id=%s", vendor.id)
