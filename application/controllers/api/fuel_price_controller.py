"""
Fuel Price Controller — endpoints for managing vendor fuel prices (with Redis cache).
"""

from fastapi import APIRouter, BackgroundTasks, Depends, status
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
from application.core.redis import get_redis
from application.core.cache import INVALIDATE_ON_FUEL_PRICE_CHANGE, CacheKey, CacheTTL
from application.services.cache_service import CacheService
from application.services.notification_service import NotificationService

router = APIRouter(prefix="/fuel-prices", tags=["Fuel Prices"])


@router.get(
    "",
    response_model=FuelPriceGlobalListResponseDTO,
    summary="Get all fuel prices globally",
)
async def get_all_prices(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """Returns all fuel prices in the system, newest first (cached 3 min)."""
    cache = CacheService(redis)
    cached = await cache.get_fuel_prices()
    if cached is not None:
        return cached
    result = await FuelPriceUsecase(db).get_all_prices()
    await cache.set_fuel_prices(result)
    return result


@router.post(
    "",
    response_model=FuelPriceResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new fuel price for a vendor",
)
async def create_fuel_price(
    dto: FuelPriceCreateDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """
    Set a new fuel price for a vendor. Each entry is tracked historically.
    The latest entry (by `effective_date`) is used automatically in transactions.
    """
    result = await FuelPriceUsecase(db).create_price(dto)

    async def _post_create():
        cache = CacheService(redis)
        await cache.delete_many_patterns(INVALIDATE_ON_FUEL_PRICE_CHANGE)
        notif = NotificationService(redis)
        await notif.notify_price_update("Vendor", float(result.price_per_liter))

    background_tasks.add_task(_post_create)
    return result


@router.put(
    "/{price_id}",
    response_model=FuelPriceResponseDTO,
    summary="Update a fuel price record",
)
async def update_fuel_price(
    price_id: int,
    dto: FuelPriceUpdateDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """
    Update an existing price entry (e.g., correct a typo).
    To add a new price point, use POST instead.
    """
    result = await FuelPriceUsecase(db).update_price(price_id, dto)

    async def _post_update():
        cache = CacheService(redis)
        await cache.delete_many_patterns(INVALIDATE_ON_FUEL_PRICE_CHANGE)
        notif = NotificationService(redis)
        await notif.notify_price_update("Vendor", float(result.price_per_liter))

    background_tasks.add_task(_post_update)
    return result


@router.get(
    "/latest/{vendor_id}",
    response_model=FuelPriceResponseDTO,
    summary="Get the latest fuel price for a vendor",
)
async def get_latest_price(
    vendor_id: int,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """Returns the most recent fuel price for the given vendor (cached 3 min)."""
    cache = CacheService(redis)
    cached = await cache.get(CacheKey.latest_price(vendor_id))
    if cached is not None:
        return cached
    result = await FuelPriceUsecase(db).get_latest_price(vendor_id)
    await cache.set(CacheKey.latest_price(vendor_id), result, CacheTTL.FUEL_PRICE_LIST)
    return result


@router.get(
    "/history/{vendor_id}",
    response_model=FuelPriceListResponseDTO,
    summary="Get full fuel price history for a vendor",
)
async def get_price_history(
    vendor_id: int,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """Returns all price entries for a vendor, newest first (cached 3 min)."""
    cache = CacheService(redis)
    cached = await cache.get(CacheKey.price_history(vendor_id))
    if cached is not None:
        return cached
    result = await FuelPriceUsecase(db).get_price_history(vendor_id)
    await cache.set(CacheKey.price_history(vendor_id), result, CacheTTL.FUEL_PRICE_LIST)
    return result


@router.delete(
    "/{price_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a fuel price record",
)
async def delete_fuel_price(
    price_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    result = await FuelPriceUsecase(db).delete_price(price_id)
    background_tasks.add_task(CacheService(redis).delete_many_patterns, INVALIDATE_ON_FUEL_PRICE_CHANGE)
    return result
