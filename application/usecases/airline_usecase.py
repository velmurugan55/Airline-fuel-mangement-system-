"""
Airline Use Cases — business logic for airline management.
"""

from typing import List
from sqlalchemy.orm import Session

from application.repositories.airline_repository import AirlineRepository
from application.dto.airline_dto import AirlineCreateDTO, AirlineUpdateDTO, AirlineResponseDTO, AirlineListResponseDTO
from application.exception.not_found_exception import NotFoundException
from application.exception.custom_exception import ConflictException
import logging

logger = logging.getLogger(__name__)


class AirlineUsecase:

    def __init__(self, db: Session):
        self.repo = AirlineRepository(db)

    async def create_airline(self, dto: AirlineCreateDTO) -> AirlineResponseDTO:
        existing = self.repo.get_by_code(dto.airline_code)
        if existing:
            raise ConflictException(f"Airline with code '{dto.airline_code}' already exists.")
        airline = self.repo.create(dto)
        return AirlineResponseDTO.model_validate(airline)

    async def update_airline(self, airline_id: int, dto: AirlineUpdateDTO) -> AirlineResponseDTO:
        airline = self.repo.get_by_id(airline_id)
        if not airline:
            raise NotFoundException("Airline", airline_id)
        updated = self.repo.update(airline, dto)
        return AirlineResponseDTO.model_validate(updated)

    async def delete_airline(self, airline_id: int) -> dict:
        airline = self.repo.get_by_id(airline_id)
        if not airline:
            raise NotFoundException("Airline", airline_id)
        self.repo.delete(airline)
        return {"message": f"Airline id={airline_id} deleted successfully."}

    async def get_airline(self, airline_id: int) -> AirlineResponseDTO:
        airline = self.repo.get_by_id(airline_id)
        if not airline:
            raise NotFoundException("Airline", airline_id)
        return AirlineResponseDTO.model_validate(airline)

    async def get_all_airlines(self) -> AirlineListResponseDTO:
        airlines = self.repo.get_all()
        return AirlineListResponseDTO(
            total=len(airlines),
            data=[AirlineResponseDTO.model_validate(a) for a in airlines],
        )
