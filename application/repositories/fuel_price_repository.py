"""
Fuel Price Repository — DB operations for the FuelPrice model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from application.src.models.fuel_price_model import FuelPrice
from application.dto.fuel_price_dto import FuelPriceCreateDTO, FuelPriceUpdateDTO
import logging

logger = logging.getLogger(__name__)


class FuelPriceRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, price_id: int) -> Optional[FuelPrice]:
        return self.db.query(FuelPrice).filter(FuelPrice.id == price_id).first()

    def get_latest_by_vendor(self, vendor_id: int) -> Optional[FuelPrice]:
        """
        Returns the most recent FuelPrice for a vendor
        (ordered by effective_date DESC, then id DESC as tiebreaker).
        """
        return (
            self.db.query(FuelPrice)
            .filter(FuelPrice.vendor_id == vendor_id)
            .order_by(FuelPrice.effective_date.desc(), FuelPrice.id.desc())
            .first()
        )

    def get_history_by_vendor(self, vendor_id: int) -> List[FuelPrice]:
        """
        Returns full price history for a vendor, newest first.
        """
        return (
            self.db.query(FuelPrice)
            .filter(FuelPrice.vendor_id == vendor_id)
            .order_by(FuelPrice.effective_date.desc(), FuelPrice.id.desc())
            .all()
        )

    def create(self, dto: FuelPriceCreateDTO) -> FuelPrice:
        price = FuelPrice(**dto.model_dump())
        self.db.add(price)
        self.db.commit()
        self.db.refresh(price)
        logger.info(
            "Created fuel price: vendor_id=%s price=%s date=%s",
            price.vendor_id, price.price_per_liter, price.effective_date,
        )
        return price

    def update(self, price: FuelPrice, dto: FuelPriceUpdateDTO) -> FuelPrice:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(price, field, value)
        self.db.commit()
        self.db.refresh(price)
        logger.info("Updated fuel price id=%s", price.id)
        return price
