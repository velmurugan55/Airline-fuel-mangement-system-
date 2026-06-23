"""
Fuel Price Use Cases — business logic for fuel price management.

Business Rules Enforced:
  - Rule #2: Latest fuel price is auto-selected by effective_date DESC.
"""

from sqlalchemy.orm import Session

from application.repositories.fuel_price_repository import FuelPriceRepository
from application.repositories.vendor_repository import VendorRepository
from application.dto.fuel_price_dto import (
    FuelPriceCreateDTO,
    FuelPriceUpdateDTO,
    FuelPriceResponseDTO,
    FuelPriceListResponseDTO,
)
from application.exception.not_found_exception import NotFoundException
import logging

logger = logging.getLogger(__name__)


class FuelPriceUsecase:

    def __init__(self, db: Session):
        self.repo = FuelPriceRepository(db)
        self.vendor_repo = VendorRepository(db)

    async def create_price(self, dto: FuelPriceCreateDTO) -> FuelPriceResponseDTO:
        # Verify vendor exists
        vendor = self.vendor_repo.get_by_id(dto.vendor_id)
        if not vendor:
            raise NotFoundException("Vendor", dto.vendor_id)
        price = self.repo.create(dto)
        return FuelPriceResponseDTO.model_validate(price)

    async def update_price(self, price_id: int, dto: FuelPriceUpdateDTO) -> FuelPriceResponseDTO:
        price = self.repo.get_by_id(price_id)
        if not price:
            raise NotFoundException("FuelPrice", price_id)
        updated = self.repo.update(price, dto)
        return FuelPriceResponseDTO.model_validate(updated)

    async def get_latest_price(self, vendor_id: int) -> FuelPriceResponseDTO:
        """
        Business Rule #2: Automatically returns the latest fuel price
        for the given vendor, ordered by effective_date DESC.
        """
        vendor = self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)
        price = self.repo.get_latest_by_vendor(vendor_id)
        if not price:
            raise NotFoundException("FuelPrice", f"vendor_id={vendor_id}")
        return FuelPriceResponseDTO.model_validate(price)

    async def get_price_history(self, vendor_id: int) -> FuelPriceListResponseDTO:
        vendor = self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)
        prices = self.repo.get_history_by_vendor(vendor_id)
        return FuelPriceListResponseDTO(
            vendor_id=vendor_id,
            history=[FuelPriceResponseDTO.model_validate(p) for p in prices],
        )
