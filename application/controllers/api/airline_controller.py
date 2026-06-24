"""
Airline Controller — CRUD endpoints for airlines (with Redis cache).
"""

import os, shutil
from fastapi import APIRouter, BackgroundTasks, Depends, status, UploadFile, File
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
from application.core.redis import get_redis
from application.core.cache import INVALIDATE_ON_AIRLINE_CHANGE, CacheKey, CacheTTL
from application.services.cache_service import CacheService

router = APIRouter(prefix="/airlines", tags=["Airlines"])


@router.post(
    "",
    response_model=AirlineResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new airline",
)
async def create_airline(
    dto: AirlineCreateDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    result = await AirlineUsecase(db).create_airline(dto)
    background_tasks.add_task(CacheService(redis).delete_many_patterns, INVALIDATE_ON_AIRLINE_CHANGE)
    return result


@router.get(
    "",
    response_model=AirlineListResponseDTO,
    summary="Get all airlines",
)
async def get_all_airlines(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """Returns a paginated list of all registered airlines (cached 5 min)."""
    cache = CacheService(redis)
    cached = await cache.get_airlines()
    if cached is not None:
        return cached
    result = await AirlineUsecase(db).get_all_airlines()
    await cache.set_airlines(result)
    return result


@router.get(
    "/{airline_id}",
    response_model=AirlineResponseDTO,
    summary="Get airline by ID",
)
async def get_airline(
    airline_id: int,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    cache = CacheService(redis)
    cached = await cache.get(CacheKey.airline(airline_id))
    if cached is not None:
        return cached
    result = await AirlineUsecase(db).get_airline(airline_id)
    await cache.set(CacheKey.airline(airline_id), result, CacheTTL.AIRLINE_LIST)
    return result


@router.put(
    "/{airline_id}",
    response_model=AirlineResponseDTO,
    summary="Update an airline",
)
async def update_airline(
    airline_id: int,
    dto: AirlineUpdateDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    result = await AirlineUsecase(db).update_airline(airline_id, dto)
    invalidate = INVALIDATE_ON_AIRLINE_CHANGE + [CacheKey.airline(airline_id)]
    background_tasks.add_task(CacheService(redis).delete_many_patterns, invalidate)
    return result


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/{airline_id}/logo",
    response_model=AirlineResponseDTO,
    summary="Upload airline logo",
)
async def upload_logo(
    airline_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1] or ".png"
    filename = f"airline_{airline_id}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = await AirlineUsecase(db).update_logo(airline_id, f"/static/uploads/{filename}")
    background_tasks.add_task(CacheService(redis).delete, CacheKey.airline(airline_id), CacheKey.AIRLINE_LIST)
    return result


@router.delete(
    "/{airline_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an airline",
)
async def delete_airline(
    airline_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    result = await AirlineUsecase(db).delete_airline(airline_id)
    invalidate = INVALIDATE_ON_AIRLINE_CHANGE + [CacheKey.airline(airline_id)]
    background_tasks.add_task(CacheService(redis).delete_many_patterns, invalidate)
    return result
