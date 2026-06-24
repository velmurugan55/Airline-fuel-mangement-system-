"""
User SQLAlchemy Model.
`role` (SAEnum) kept for JWT backward-compatibility.
`role_id` FK drives the new RBAC permission system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from application.providers.database import Base
import enum


class UserRole(str, enum.Enum):
    admin    = "admin"
    operator = "operator"
    viewer   = "viewer"


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(SAEnum(UserRole), nullable=False, default=UserRole.operator)  # legacy JWT claim

    # RBAC extended fields
    first_name    = Column(String(100), nullable=True)
    last_name     = Column(String(100), nullable=True)
    phone_number  = Column(String(30),  nullable=True)
    email         = Column(String(255), unique=True, nullable=True, index=True)
    role_id       = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    is_active     = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to Role ORM model
    role_entity   = relationship("Role", back_populates="users", lazy="select")

    @property
    def full_name(self) -> str:
        parts = filter(None, [self.first_name, self.last_name])
        return " ".join(parts) or self.username

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"
