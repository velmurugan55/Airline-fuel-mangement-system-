"""
Role Use Cases — CRUD for roles.
"""

from sqlalchemy.orm import Session
from application.repositories.role_repository import RoleRepository
from application.repositories.audit_log_repository import AuditLogRepository
from application.dto.role_dto import RoleCreateDTO, RoleUpdateDTO, RoleResponseDTO, RoleListResponseDTO
from application.exception.custom_exception import ConflictException
from application.exception.not_found_exception import NotFoundException


class RoleUsecase:
    def __init__(self, db: Session):
        self.repo  = RoleRepository(db)
        self.audit = AuditLogRepository(db)

    async def create_role(self, dto: RoleCreateDTO, actor_id: int = None, ip: str = None) -> RoleResponseDTO:
        if self.repo.get_by_name(dto.role_name):
            raise ConflictException(f"Role '{dto.role_name}' already exists.")
        role = self.repo.create(dto)
        self.audit.log("CREATE_ROLE", user_id=actor_id, entity_type="role", entity_id=role.id,
                       new_value={"role_name": role.role_name}, ip_address=ip)
        return RoleResponseDTO.model_validate(role)

    async def update_role(self, role_id: int, dto: RoleUpdateDTO, actor_id: int = None, ip: str = None) -> RoleResponseDTO:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role", role_id)
        if dto.role_name and dto.role_name != role.role_name and self.repo.get_by_name(dto.role_name):
            raise ConflictException(f"Role '{dto.role_name}' already exists.")
        old = {"role_name": role.role_name, "is_active": role.is_active}
        updated = self.repo.update(role, dto)
        self.audit.log("UPDATE_ROLE", user_id=actor_id, entity_type="role", entity_id=role_id,
                       old_value=old, new_value=dto.model_dump(exclude_none=True), ip_address=ip)
        return RoleResponseDTO.model_validate(updated)

    async def delete_role(self, role_id: int, actor_id: int = None, ip: str = None) -> dict:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role", role_id)
        self.repo.delete(role)
        self.audit.log("DELETE_ROLE", user_id=actor_id, entity_type="role", entity_id=role_id, ip_address=ip)
        return {"message": f"Role '{role.role_name}' deleted."}

    async def get_role(self, role_id: int) -> RoleResponseDTO:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role", role_id)
        return RoleResponseDTO.model_validate(role)

    async def get_all_roles(self) -> RoleListResponseDTO:
        roles = self.repo.get_all()
        return RoleListResponseDTO(total=len(roles), data=[RoleResponseDTO.model_validate(r) for r in roles])
