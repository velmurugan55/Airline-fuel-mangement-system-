"""
Vendor Controller — CRUD endpoints for fuel vendors (with Redis cache).
"""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.vendor_usecase import VendorUsecase
from application.dto.vendor_dto import (
    VendorCreateDTO,
    VendorUpdateDTO,
    VendorResponseDTO,
    VendorListResponseDTO,
)
from application.core.redis import get_redis
from application.core.cache import INVALIDATE_ON_VENDOR_CHANGE, CacheKey, CacheTTL
from application.services.cache_service import CacheService

router = APIRouter(prefix="/vendors", tags=["Fuel Vendors"])


@router.post(
    "",
    response_model=VendorResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new fuel vendor",
)
async def create_vendor(
    dto: VendorCreateDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    result = await VendorUsecase(db).create_vendor(dto)
    background_tasks.add_task(CacheService(redis).delete_many_patterns, INVALIDATE_ON_VENDOR_CHANGE)
    return result


@router.get(
    "",
    response_model=VendorListResponseDTO,
    summary="List all fuel vendors",
)
async def get_all_vendors(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    cache = CacheService(redis)
    cached = await cache.get_vendors()
    if cached is not None:
        return cached
    result = await VendorUsecase(db).get_all_vendors()
    await cache.set_vendors(result)
    return result


@router.get(
    "/{vendor_id}",
    response_model=VendorResponseDTO,
    summary="Get fuel vendor by ID",
)
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    cache = CacheService(redis)
    cached = await cache.get(CacheKey.vendor(vendor_id))
    if cached is not None:
        return cached
    result = await VendorUsecase(db).get_vendor(vendor_id)
    await cache.set(CacheKey.vendor(vendor_id), result, CacheTTL.VENDOR_LIST)
    return result


@router.put(
    "/{vendor_id}",
    response_model=VendorResponseDTO,
    summary="Update a fuel vendor",
)
async def update_vendor(
    vendor_id: int,
    dto: VendorUpdateDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    result = await VendorUsecase(db).update_vendor(vendor_id, dto)
    invalidate = INVALIDATE_ON_VENDOR_CHANGE + [CacheKey.vendor(vendor_id)]
    background_tasks.add_task(CacheService(redis).delete_many_patterns, invalidate)
    return result


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a fuel vendor",
)
async def delete_vendor(
    vendor_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    result = await VendorUsecase(db).delete_vendor(vendor_id)
    invalidate = INVALIDATE_ON_VENDOR_CHANGE + [CacheKey.vendor(vendor_id)]
    background_tasks.add_task(CacheService(redis).delete_many_patterns, invalidate)
    return result
