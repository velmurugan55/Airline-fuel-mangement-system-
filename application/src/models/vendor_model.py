"""
Fuel Vendor SQLAlchemy Model.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from application.providers.database import Base


class FuelVendor(Base):
    __tablename__ = "fuel_vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_code = Column(String(20), unique=True, nullable=False, index=True)
    vendor_name = Column(String(200), nullable=False)
    contact_person = Column(String(150), nullable=True)
    email = Column(String(254), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(500), nullable=True)

    # One vendor -> many fuel prices
    fuel_prices = relationship("FuelPrice", back_populates="vendor", lazy="select")
    # One vendor -> many transactions
    transactions = relationship("FuelTransaction", back_populates="vendor", lazy="select")

    def __repr__(self) -> str:
        return f"<FuelVendor id={self.id} code={self.vendor_code} name={self.vendor_name}>"
