"""
Role Controller — CRUD for roles.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.role_usecase import RoleUsecase
from application.dto.role_dto import RoleCreateDTO, RoleUpdateDTO, RoleResponseDTO, RoleListResponseDTO
from application.src.models.user_model import User

router = APIRouter(prefix="/roles", tags=["Role Management"])


def _ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.get("", response_model=RoleListResponseDTO, summary="List all roles")
async def list_roles(
    db: Session = Depends(get_db),
    _:  User    = Depends(get_current_user),
):
    return await RoleUsecase(db).get_all_roles()


@router.post("", response_model=RoleResponseDTO, status_code=status.HTTP_201_CREATED, summary="Create role")
async def create_role(
    dto:     RoleCreateDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await RoleUsecase(db).create_role(dto, actor_id=actor.id, ip=_ip(request))


@router.get("/{role_id}", response_model=RoleResponseDTO, summary="Get role by ID")
async def get_role(
    role_id: int,
    db:      Session = Depends(get_db),
    _:       User    = Depends(get_current_user),
):
    return await RoleUsecase(db).get_role(role_id)


@router.put("/{role_id}", response_model=RoleResponseDTO, summary="Update role")
async def update_role(
    role_id: int,
    dto:     RoleUpdateDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await RoleUsecase(db).update_role(role_id, dto, actor_id=actor.id, ip=_ip(request))


@router.delete("/{role_id}", summary="Delete role")
async def delete_role(
    role_id: int,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await RoleUsecase(db).delete_role(role_id, actor_id=actor.id, ip=_ip(request))
