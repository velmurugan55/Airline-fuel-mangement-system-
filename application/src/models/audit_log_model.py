"""
AuditLog SQLAlchemy Model — tracks create/update/delete/permission changes.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from application.providers.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action      = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True)
    entity_id   = Column(Integer, nullable=True)
    old_value   = Column(JSON, nullable=True)
    new_value   = Column(JSON, nullable=True)
    ip_address  = Column(String(45), nullable=True)
    description = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action} entity={self.entity_type}:{self.entity_id}>"
