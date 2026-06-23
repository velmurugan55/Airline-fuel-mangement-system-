"""
Fuel Transaction SQLAlchemy Model.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, Text
from sqlalchemy.orm import relationship
from application.providers.database import Base


class FuelTransaction(Base):
    __tablename__ = "fuel_transactions"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), unique=True, nullable=False, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.id", ondelete="RESTRICT"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("fuel_vendors.id", ondelete="RESTRICT"), nullable=False, index=True)
    fuel_quantity = Column(Numeric(14, 4), nullable=False)   # liters
    fuel_price = Column(Numeric(12, 4), nullable=False)      # price per liter at time of transaction
    total_amount = Column(Numeric(18, 4), nullable=False)    # fuel_quantity × fuel_price
    transaction_date = Column(Date, nullable=False, index=True)
    remarks = Column(Text, nullable=True)

    # Relationships for eager loading in reports
    airline = relationship("Airline", back_populates="transactions")
    vendor = relationship("FuelVendor", back_populates="transactions")

    def __repr__(self) -> str:
        return (
            f"<FuelTransaction id={self.id} invoice={self.invoice_no} "
            f"amount={self.total_amount}>"
        )
