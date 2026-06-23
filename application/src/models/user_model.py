"""
User SQLAlchemy Model.
"""

from sqlalchemy import Column, Integer, String, Enum as SAEnum
from application.providers.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    operator = "operator"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.operator)

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"
