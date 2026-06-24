"""
User Controller — CRUD + activate/deactivate + password reset.
"""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.user_usecase import UserUsecase
from application.dto.user_dto import (
    UserCreateDTO, UserUpdateDTO, UserResetPasswordDTO,
    UserResponseDTO, UserListResponseDTO,
)
from application.src.models.user_model import User

router = APIRouter(prefix="/users", tags=["User Management"])


def _ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.get("", response_model=UserListResponseDTO, summary="List all users")
async def list_users(
    page:   int = Query(1, ge=1),
    limit:  int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search by username, name, or email"),
    db:     Session = Depends(get_db),
    _:      User    = Depends(get_current_user),
):
    return await UserUsecase(db).get_all_users(page=page, limit=limit, search=search)


@router.post("", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED, summary="Create user")
async def create_user(
    dto:     UserCreateDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await UserUsecase(db).create_user(dto, actor_id=actor.id, ip=_ip(request))


@router.get("/{user_id}", response_model=UserResponseDTO, summary="Get user by ID")
async def get_user(
    user_id: int,
    db:      Session = Depends(get_db),
    _:       User    = Depends(get_current_user),
):
    return await UserUsecase(db).get_user(user_id)


@router.put("/{user_id}", response_model=UserResponseDTO, summary="Update user")
async def update_user(
    user_id: int,
    dto:     UserUpdateDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await UserUsecase(db).update_user(user_id, dto, actor_id=actor.id, ip=_ip(request))


@router.post("/{user_id}/activate", response_model=UserResponseDTO, summary="Activate user")
async def activate_user(
    user_id: int,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await UserUsecase(db).activate_user(user_id, actor_id=actor.id, ip=_ip(request))


@router.post("/{user_id}/deactivate", response_model=UserResponseDTO, summary="Deactivate user")
async def deactivate_user(
    user_id: int,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await UserUsecase(db).deactivate_user(user_id, actor_id=actor.id, ip=_ip(request))


@router.post("/{user_id}/reset-password", summary="Reset user password")
async def reset_password(
    user_id: int,
    dto:     UserResetPasswordDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await UserUsecase(db).reset_password(user_id, dto, actor_id=actor.id, ip=_ip(request))
