"""
Airline Controller — CRUD endpoints for airlines.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.airline_usecase import AirlineUsecase
from application.dto.airline_dto import (
    AirlineCreateDTO,
    AirlineUpdateDTO,
    AirlineResponseDTO,
    AirlineListResponseDTO,
)

router = APIRouter(prefix="/airlines", tags=["Airlines"])


@router.post(
    "",
    response_model=AirlineResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new airline",
)
async def create_airline(
    dto: AirlineCreateDTO,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Register a new airline in the system.

    **Sample Request:**
    ```json
    {
      "airline_code": "GA",
      "airline_name": "Garuda Indonesia",
      "contact_person": "John Doe",
      "email": "ops@garuda.com",
      "phone": "+62-21-2351-9999",
      "address": "Soekarno-Hatta Airport, Tangerang"
    }
    ```
    """
    return await AirlineUsecase(db).create_airline(dto)


@router.get(
    "",
    response_model=AirlineListResponseDTO,
    summary="Get all airlines",
)
async def get_all_airlines(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Returns a paginated list of all registered airlines."""
    return await AirlineUsecase(db).get_all_airlines()


@router.get(
    "/{airline_id}",
    response_model=AirlineResponseDTO,
    summary="Get airline by ID",
)
async def get_airline(
    airline_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return await AirlineUsecase(db).get_airline(airline_id)


@router.put(
    "/{airline_id}",
    response_model=AirlineResponseDTO,
    summary="Update an airline",
)
async def update_airline(
    airline_id: int,
    dto: AirlineUpdateDTO,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Partially update airline fields. Only provided fields will be modified.

    **Sample Request:**
    ```json
    {
      "email": "newemail@garuda.com",
      "phone": "+62-21-9999-0000"
    }
    ```
    """
    return await AirlineUsecase(db).update_airline(airline_id, dto)


@router.delete(
    "/{airline_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an airline",
)
async def delete_airline(
    airline_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return await AirlineUsecase(db).delete_airline(airline_id)
