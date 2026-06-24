"""
Menu Use Cases — CRUD for sidebar menus.
"""

from sqlalchemy.orm import Session
from application.repositories.menu_repository import MenuRepository
from application.repositories.audit_log_repository import AuditLogRepository
from application.dto.menu_dto import MenuCreateDTO, MenuUpdateDTO, MenuResponseDTO, MenuListResponseDTO
from application.exception.custom_exception import ConflictException
from application.exception.not_found_exception import NotFoundException


class MenuUsecase:
    def __init__(self, db: Session):
        self.repo  = MenuRepository(db)
        self.audit = AuditLogRepository(db)

    async def create_menu(self, dto: MenuCreateDTO, actor_id: int = None, ip: str = None) -> MenuResponseDTO:
        if self.repo.get_by_code(dto.menu_code):
            raise ConflictException(f"Menu code '{dto.menu_code}' already exists.")
        menu = self.repo.create(dto)
        self.audit.log("CREATE_MENU", user_id=actor_id, entity_type="menu", entity_id=menu.id,
                       new_value={"menu_code": menu.menu_code}, ip_address=ip)
        return MenuResponseDTO.model_validate(menu)

    async def update_menu(self, menu_id: int, dto: MenuUpdateDTO, actor_id: int = None, ip: str = None) -> MenuResponseDTO:
        menu = self.repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("Menu", menu_id)
        updated = self.repo.update(menu, dto)
        self.audit.log("UPDATE_MENU", user_id=actor_id, entity_type="menu", entity_id=menu_id,
                       new_value=dto.model_dump(exclude_none=True), ip_address=ip)
        return MenuResponseDTO.model_validate(updated)

    async def delete_menu(self, menu_id: int, actor_id: int = None, ip: str = None) -> dict:
        menu = self.repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("Menu", menu_id)
        self.repo.delete(menu)
        self.audit.log("DELETE_MENU", user_id=actor_id, entity_type="menu", entity_id=menu_id, ip_address=ip)
        return {"message": f"Menu '{menu.menu_name}' deleted."}

    async def get_menu(self, menu_id: int) -> MenuResponseDTO:
        menu = self.repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("Menu", menu_id)
        return MenuResponseDTO.model_validate(menu)

    async def get_all_menus(self) -> MenuListResponseDTO:
        menus = self.repo.get_all()
        return MenuListResponseDTO(total=len(menus), data=[MenuResponseDTO.model_validate(m) for m in menus])
