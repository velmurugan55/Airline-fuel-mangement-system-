"""
Permission Controller — assign + query role-menu permissions, sidebar API.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.permission_usecase import PermissionUsecase
from application.dto.permission_dto import (
    RoleMenuPermissionUpdateDTO, PermissionResponseDTO, UserPermissionsResponseDTO,
)
from application.src.models.user_model import User

router = APIRouter(prefix="/permissions", tags=["Permission Management"])


@router.get(
    "/roles/{role_id}",
    response_model=List[PermissionResponseDTO],
    summary="Get all permissions for a role",
)
async def get_role_permissions(
    role_id: int,
    db:      Session = Depends(get_db),
    _:       User    = Depends(get_current_user),
):
    return await PermissionUsecase(db).get_role_permissions(role_id)


@router.put(
    "/roles/{role_id}",
    summary="Bulk-assign permissions to a role (replaces all existing)",
)
async def assign_permissions(
    role_id: int,
    dto:     RoleMenuPermissionUpdateDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    ip = request.client.host if request.client else "unknown"
    return await PermissionUsecase(db).assign_permissions(role_id, dto, actor_id=actor.id, ip=ip)


@router.get(
    "/me/sidebar",
    response_model=UserPermissionsResponseDTO,
    summary="Get sidebar + permissions for the logged-in user",
)
async def get_my_sidebar(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Called on every app load to rebuild the sidebar and permission context.
    Returns all menus the user can view, plus all 8 permission flags per menu.
    """
    if current_user.role_id is None:
        return UserPermissionsResponseDTO(
            role_id=None, role_name=str(current_user.role.value), menus=[], permissions={}
        )
    role = current_user.role_entity
    role_name = role.role_name if role else str(current_user.role.value)
    return await PermissionUsecase(db).get_user_sidebar(current_user.role_id, role_name)
