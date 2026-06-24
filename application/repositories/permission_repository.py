"""
Permission Repository — DB operations for RoleMenuPermission.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from application.src.models.role_menu_permission_model import RoleMenuPermission
from application.src.models.menu_model import Menu
from application.dto.permission_dto import MenuPermissionEntryDTO, SidebarMenuDTO, PermissionSetDTO


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, role_id: int, menu_id: int) -> Optional[RoleMenuPermission]:
        return (
            self.db.query(RoleMenuPermission)
            .filter(RoleMenuPermission.role_id == role_id, RoleMenuPermission.menu_id == menu_id)
            .first()
        )

    def get_by_menu_code(self, role_id: int, menu_code: str) -> Optional[RoleMenuPermission]:
        return (
            self.db.query(RoleMenuPermission)
            .join(Menu, RoleMenuPermission.menu_id == Menu.id)
            .filter(RoleMenuPermission.role_id == role_id, Menu.menu_code == menu_code)
            .first()
        )

    def get_all_for_role(self, role_id: int) -> List[RoleMenuPermission]:
        return (
            self.db.query(RoleMenuPermission)
            .options(joinedload(RoleMenuPermission.menu))
            .filter(RoleMenuPermission.role_id == role_id)
            .all()
        )

    def upsert(self, role_id: int, entry: MenuPermissionEntryDTO) -> RoleMenuPermission:
        perm = self.get(role_id, entry.menu_id)
        if perm:
            for field in ["can_view", "can_create", "can_edit", "can_delete",
                          "can_download", "can_approve", "can_export", "can_print"]:
                setattr(perm, field, getattr(entry, field))
        else:
            perm = RoleMenuPermission(role_id=role_id, **entry.model_dump())
            self.db.add(perm)
        self.db.commit()
        self.db.refresh(perm)
        return perm

    def bulk_upsert(self, role_id: int, entries: List[MenuPermissionEntryDTO]) -> List[RoleMenuPermission]:
        return [self.upsert(role_id, entry) for entry in entries]

    def delete_all_for_role(self, role_id: int) -> None:
        self.db.query(RoleMenuPermission).filter(RoleMenuPermission.role_id == role_id).delete()
        self.db.commit()

    def build_sidebar_payload(self, role_id: int) -> dict:
        """
        Returns two structures used in the login response:
        - `menus`: flat list of SidebarMenuDTO (only menus where can_view=True)
        - `permissions`: dict keyed by menu_code with all 8 permission flags
        """
        records = self.get_all_for_role(role_id)

        permissions: dict = {}
        flat_menus: list = []

        for perm in records:
            menu = perm.menu
            if menu is None or not menu.is_active:
                continue

            perm_dict = perm.as_dict()
            permissions[menu.menu_code] = PermissionSetDTO(**perm_dict)

            if perm.can_view:
                flat_menus.append(SidebarMenuDTO(
                    menu_id=menu.id,
                    menu_name=menu.menu_name,
                    menu_code=menu.menu_code,
                    parent_menu_id=menu.parent_menu_id,
                    route_path=menu.route_path,
                    icon=menu.icon,
                    display_order=menu.display_order,
                    **perm_dict,
                ))

        # Sort flat menus by display_order
        flat_menus.sort(key=lambda m: m.display_order)

        return {"menus": flat_menus, "permissions": permissions}
