"""
User Use Cases — full CRUD + activate/deactivate + password reset.
"""

import logging
from sqlalchemy.orm import Session

from application.repositories.user_repository import UserRepository
from application.repositories.audit_log_repository import AuditLogRepository
from application.dto.user_dto import (
    UserCreateDTO, UserUpdateDTO, UserResetPasswordDTO,
    UserResponseDTO, UserListResponseDTO,
)
from application.exception.custom_exception import ConflictException, BadRequestException
from application.exception.not_found_exception import NotFoundException

logger = logging.getLogger(__name__)


class UserUsecase:
    def __init__(self, db: Session):
        self.repo  = UserRepository(db)
        self.audit = AuditLogRepository(db)

    async def create_user(self, dto: UserCreateDTO, actor_id: int = None, ip: str = None) -> UserResponseDTO:
        if self.repo.get_by_username(dto.username):
            raise ConflictException(f"Username '{dto.username}' already exists.")
        if dto.email and self.repo.get_by_email(dto.email):
            raise ConflictException(f"Email '{dto.email}' already in use.")
        user = self.repo.create_full_user(dto)
        self.audit.log("CREATE_USER", user_id=actor_id, entity_type="user", entity_id=user.id,
                       new_value={"username": user.username}, ip_address=ip)
        return UserResponseDTO.model_validate(user)

    async def update_user(self, user_id: int, dto: UserUpdateDTO, actor_id: int = None, ip: str = None) -> UserResponseDTO:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        if dto.email and dto.email != user.email and self.repo.get_by_email(dto.email):
            raise ConflictException(f"Email '{dto.email}' already in use.")
        old = {"role_id": user.role_id, "is_active": user.is_active}
        updated = self.repo.update_user(user, dto)
        self.audit.log("UPDATE_USER", user_id=actor_id, entity_type="user", entity_id=user_id,
                       old_value=old, new_value=dto.model_dump(exclude_none=True), ip_address=ip)
        return UserResponseDTO.model_validate(updated)

    async def get_user(self, user_id: int) -> UserResponseDTO:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return UserResponseDTO.model_validate(user)

    async def get_all_users(self, page: int = 1, limit: int = 20, search: str = "") -> UserListResponseDTO:
        users, total = self.repo.get_all(page=page, limit=limit, search=search)
        return UserListResponseDTO(
            total=total, page=page, limit=limit,
            data=[UserResponseDTO.model_validate(u) for u in users],
        )

    async def activate_user(self, user_id: int, actor_id: int = None, ip: str = None) -> UserResponseDTO:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        self.repo.set_active(user, True)
        self.audit.log("ACTIVATE_USER", user_id=actor_id, entity_type="user", entity_id=user_id, ip_address=ip)
        return UserResponseDTO.model_validate(user)

    async def deactivate_user(self, user_id: int, actor_id: int = None, ip: str = None) -> UserResponseDTO:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        self.repo.set_active(user, False)
        self.audit.log("DEACTIVATE_USER", user_id=actor_id, entity_type="user", entity_id=user_id, ip_address=ip)
        return UserResponseDTO.model_validate(user)

    async def delete_user(self, user_id: int, actor_id: int = None, ip: str = None) -> dict:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        self.repo.delete_user(user)
        self.audit.log("DELETE_USER", user_id=actor_id, entity_type="user", entity_id=user_id,
                       old_value={"username": user.username}, ip_address=ip)
        return {"message": f"User '{user.username}' deleted."}

    async def reset_password(self, user_id: int, dto: UserResetPasswordDTO, actor_id: int = None, ip: str = None) -> dict:
        if dto.new_password != dto.confirm_password:
            raise BadRequestException("Passwords do not match.")
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        self.repo.reset_password(user, dto.new_password)
        self.audit.log("RESET_PASSWORD", user_id=actor_id, entity_type="user", entity_id=user_id, ip_address=ip)
        return {"message": f"Password reset successfully for user '{user.username}'."}
