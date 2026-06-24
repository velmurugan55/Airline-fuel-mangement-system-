"""
Permission Use Cases — assign / query role-menu permissions.
"""

from sqlalchemy.orm import Session
from application.repositories.permission_repository import PermissionRepository
from application.repositories.role_repository import RoleRepository
from application.repositories.audit_log_repository import AuditLogRepository
from application.dto.permission_dto import (
    RoleMenuPermissionUpdateDTO, PermissionResponseDTO, UserPermissionsResponseDTO,
)
from application.exception.not_found_exception import NotFoundException


class PermissionUsecase:
    def __init__(self, db: Session):
        self.repo       = PermissionRepository(db)
        self.role_repo  = RoleRepository(db)
        self.audit      = AuditLogRepository(db)

    async def assign_permissions(
        self, role_id: int, dto: RoleMenuPermissionUpdateDTO,
        actor_id: int = None, ip: str = None,
    ) -> dict:
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role", role_id)
        self.repo.delete_all_for_role(role_id)
        self.repo.bulk_upsert(role_id, dto.permissions)
        self.audit.log(
            "UPDATE_PERMISSIONS", user_id=actor_id,
            entity_type="role", entity_id=role_id,
            new_value={"menu_count": len(dto.permissions)},
            ip_address=ip,
        )
        return {"message": f"Permissions updated for role '{role.role_name}'."}

    async def get_role_permissions(self, role_id: int) -> list:
        perms = self.repo.get_all_for_role(role_id)
        return [PermissionResponseDTO.model_validate(p) for p in perms]

    async def get_user_sidebar(self, role_id: int, role_name: str) -> UserPermissionsResponseDTO:
        payload = self.repo.build_sidebar_payload(role_id)
        return UserPermissionsResponseDTO(
            role_id=role_id,
            role_name=role_name,
            menus=payload["menus"],
            permissions=payload["permissions"],
        )
