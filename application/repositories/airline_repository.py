"""
Airline Repository — DB operations for the Airline model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from application.src.models.airline_model import Airline
from application.dto.airline_dto import AirlineCreateDTO, AirlineUpdateDTO
import logging

logger = logging.getLogger(__name__)


class AirlineRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, airline_id: int) -> Optional[Airline]:
        return self.db.query(Airline).filter(Airline.id == airline_id).first()

    def get_by_code(self, airline_code: str) -> Optional[Airline]:
        return self.db.query(Airline).filter(Airline.airline_code == airline_code).first()

    def get_all(self) -> List[Airline]:
        return self.db.query(Airline).order_by(Airline.airline_name).all()

    def create(self, dto: AirlineCreateDTO) -> Airline:
        airline = Airline(**dto.model_dump())
        self.db.add(airline)
        self.db.commit()
        self.db.refresh(airline)
        logger.info("Created airline: %s (%s)", airline.airline_name, airline.airline_code)
        return airline

    def update(self, airline: Airline, dto: AirlineUpdateDTO) -> Airline:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(airline, field, value)
        self.db.commit()
        self.db.refresh(airline)
        logger.info("Updated airline id=%s", airline.id)
        return airline

    def delete(self, airline: Airline) -> None:
        self.db.delete(airline)
        self.db.commit()
        logger.info("Deleted airline id=%s", airline.id)
