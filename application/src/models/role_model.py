"""
Role SQLAlchemy Model.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from application.providers.database import Base


class Role(Base):
    __tablename__ = "roles"

    id          = Column(Integer, primary_key=True, index=True)
    role_name   = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users       = relationship("User", back_populates="role_entity", lazy="select")
    permissions = relationship("RoleMenuPermission", back_populates="role", cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.role_name}>"
