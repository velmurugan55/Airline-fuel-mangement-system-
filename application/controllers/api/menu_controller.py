"""
Menu Controller — CRUD for sidebar menus.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.menu_usecase import MenuUsecase
from application.dto.menu_dto import MenuCreateDTO, MenuUpdateDTO, MenuResponseDTO, MenuListResponseDTO
from application.src.models.user_model import User

router = APIRouter(prefix="/menus", tags=["Menu Management"])


def _ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.get("", response_model=MenuListResponseDTO, summary="List all menus")
async def list_menus(
    db: Session = Depends(get_db),
    _:  User    = Depends(get_current_user),
):
    return await MenuUsecase(db).get_all_menus()


@router.post("", response_model=MenuResponseDTO, status_code=status.HTTP_201_CREATED, summary="Create menu")
async def create_menu(
    dto:     MenuCreateDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await MenuUsecase(db).create_menu(dto, actor_id=actor.id, ip=_ip(request))


@router.get("/{menu_id}", response_model=MenuResponseDTO, summary="Get menu by ID")
async def get_menu(
    menu_id: int,
    db:      Session = Depends(get_db),
    _:       User    = Depends(get_current_user),
):
    return await MenuUsecase(db).get_menu(menu_id)


@router.put("/{menu_id}", response_model=MenuResponseDTO, summary="Update menu")
async def update_menu(
    menu_id: int,
    dto:     MenuUpdateDTO,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await MenuUsecase(db).update_menu(menu_id, dto, actor_id=actor.id, ip=_ip(request))


@router.delete("/{menu_id}", summary="Delete menu")
async def delete_menu(
    menu_id: int,
    request: Request,
    db:      Session = Depends(get_db),
    actor:   User    = Depends(get_current_user),
):
    return await MenuUsecase(db).delete_menu(menu_id, actor_id=actor.id, ip=_ip(request))
