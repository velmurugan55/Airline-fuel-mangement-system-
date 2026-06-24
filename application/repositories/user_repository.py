"""
User Repository — DB operations for the User model.
Backward-compatible: existing authenticate() logic unchanged.
"""

from typing import Optional, List, Tuple
import bcrypt

from sqlalchemy.orm import Session
from application.src.models.user_model import User, UserRole
from application.dto.user_dto import UserCreateDTO, UserUpdateDTO
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── Password Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    # ── Lookups ────────────────────────────────────────────────────────────────

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, page: int = 1, limit: int = 20, search: str = "") -> Tuple[List[User], int]:
        query = self.db.query(User)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                User.username.ilike(pattern)
                | User.first_name.ilike(pattern)
                | User.last_name.ilike(pattern)
                | User.email.ilike(pattern)
            )
        total = query.count()
        offset = (page - 1) * limit
        users = query.order_by(User.id).offset(offset).limit(limit).all()
        return users, total

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def create_user(
        self,
        username: str,
        plain_password: str,
        role: UserRole = UserRole.operator,
    ) -> User:
        """Legacy create — keeps existing seeder/migration calls working."""
        user = User(
            username=username,
            password_hash=self.hash_password(plain_password),
            role=role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("Created user: %s (role=%s)", username, role)
        return user

    def create_full_user(self, dto: UserCreateDTO) -> User:
        legacy_role = (
            UserRole.admin if dto.role == "admin"
            else UserRole.viewer if dto.role == "viewer"
            else UserRole.operator
        )
        user = User(
            username=dto.username,
            password_hash=self.hash_password(dto.password),
            role=legacy_role,
            first_name=dto.first_name,
            last_name=dto.last_name,
            phone_number=dto.phone_number,
            email=dto.email,
            role_id=dto.role_id,
            is_active=dto.is_active,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("Created full user: %s role_id=%s", dto.username, dto.role_id)
        return user

    def update_user(self, user: User, dto: UserUpdateDTO) -> User:
        update_data = dto.model_dump(exclude_none=True)
        if "role" in update_data:
            role_str = update_data.pop("role")
            user.role = (
                UserRole.admin if role_str == "admin"
                else UserRole.viewer if role_str == "viewer"
                else UserRole.operator
            )
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def reset_password(self, user: User, new_plain: str) -> User:
        user.password_hash = self.hash_password(new_plain)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_active(self, user: User, active: bool) -> User:
        user.is_active = active
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    # ── Auth (unchanged logic, adds is_active check) ───────────────────────────

    def authenticate(self, username: str, plain_password: str) -> Optional[User]:
        user = self.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(plain_password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
