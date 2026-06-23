"""
Airline SQLAlchemy Model.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from application.providers.database import Base


class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True, index=True)
    airline_code = Column(String(20), unique=True, nullable=False, index=True)
    airline_name = Column(String(200), nullable=False)
    contact_person = Column(String(150), nullable=True)
    email = Column(String(254), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(500), nullable=True)

    # One airline -> many transactions
    transactions = relationship("FuelTransaction", back_populates="airline", lazy="select")

    def __repr__(self) -> str:
        return f"<Airline id={self.id} code={self.airline_code} name={self.airline_name}>"
