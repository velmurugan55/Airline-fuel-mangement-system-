"""
User Repository — handles DB operations for the User model.
Uses bcrypt directly (bypasses passlib which is incompatible with bcrypt 4+/5+).
"""

from typing import Optional
import bcrypt

from sqlalchemy.orm import Session
from application.src.models.user_model import User, UserRole
import logging

logger = logging.getLogger(__name__)


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── Password Helpers ───────────────────────────────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        """Hash a plain-text password with bcrypt (work factor = 12)."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify a plain-text password against a stored bcrypt hash."""
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    # ── CRUD ───────────────────────────────────────────────────────────────

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(
        self,
        username: str,
        plain_password: str,
        role: UserRole = UserRole.operator,
    ) -> User:
        user = User(
            username=username,
            password_hash=self.hash_password(plain_password),
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("Created user: %s (role=%s)", username, role)
        return user

    def authenticate(self, username: str, plain_password: str) -> Optional[User]:
        """Return the User if credentials are valid, else None."""
        user = self.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(plain_password, user.password_hash):
            return None
        return user
