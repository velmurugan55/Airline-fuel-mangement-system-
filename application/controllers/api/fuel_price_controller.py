"""
Fuel Price Controller — endpoints for managing vendor fuel prices.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.fuel_price_usecase import FuelPriceUsecase
from application.dto.fuel_price_dto import (
    FuelPriceCreateDTO,
    FuelPriceUpdateDTO,
    FuelPriceResponseDTO,
    FuelPriceListResponseDTO,
    FuelPriceGlobalListResponseDTO,
)

router = APIRouter(prefix="/fuel-prices", tags=["Fuel Prices"])


@router.get(
    "",
    response_model=FuelPriceGlobalListResponseDTO,
    summary="Get all fuel prices globally",
)
async def get_all_prices(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Returns all fuel prices in the system, newest first."""
    return await FuelPriceUsecase(db).get_all_prices()


@router.post(
    "",
    response_model=FuelPriceResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new fuel price for a vendor",
)
async def create_fuel_price(
    dto: FuelPriceCreateDTO,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Set a new fuel price for a vendor. Each entry is tracked historically.
    The latest entry (by `effective_date`) is used automatically in transactions.

    **Sample Request:**
    ```json
    {
      "vendor_id": 1,
      "price_per_liter": 12500.0000,
      "effective_date": "2024-06-22"
    }
    ```
    """
    return await FuelPriceUsecase(db).create_price(dto)


@router.put(
    "/{price_id}",
    response_model=FuelPriceResponseDTO,
    summary="Update a fuel price record",
)
async def update_fuel_price(
    price_id: int,
    dto: FuelPriceUpdateDTO,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Update an existing price entry (e.g., correct a typo).
    To add a new price point, use POST instead.
    """
    return await FuelPriceUsecase(db).update_price(price_id, dto)


@router.get(
    "/latest/{vendor_id}",
    response_model=FuelPriceResponseDTO,
    summary="Get the latest fuel price for a vendor",
)
async def get_latest_price(
    vendor_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Returns the most recent fuel price for the given vendor
    (ordered by `effective_date` DESC). This is the price that will be
    automatically applied to new fuel transactions.
    """
    return await FuelPriceUsecase(db).get_latest_price(vendor_id)


@router.get(
    "/history/{vendor_id}",
    response_model=FuelPriceListResponseDTO,
    summary="Get full fuel price history for a vendor",
)
async def get_price_history(
    vendor_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Returns all price entries for a vendor, newest first."""
    return await FuelPriceUsecase(db).get_price_history(vendor_id)


@router.delete(
    "/{price_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a fuel price record",
)
async def delete_fuel_price(
    price_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return await FuelPriceUsecase(db).delete_price(price_id)
