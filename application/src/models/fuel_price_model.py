"""
Fuel Price SQLAlchemy Model.
"""

from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from application.providers.database import Base


class FuelPrice(Base):
    __tablename__ = "fuel_prices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("fuel_vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    price_per_liter = Column(Numeric(12, 4), nullable=False)
    effective_date = Column(Date, nullable=False)

    # Relationship back to vendor
    vendor = relationship("FuelVendor", back_populates="fuel_prices")

    def __repr__(self) -> str:
        return (
            f"<FuelPrice id={self.id} vendor_id={self.vendor_id} "
            f"price={self.price_per_liter} date={self.effective_date}>"
        )
