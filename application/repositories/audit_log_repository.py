"""
AuditLog Repository — write-only DB operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from application.src.models.audit_log_model import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        ip_address: Optional[str] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            description=description,
        )
        self.db.add(entry)
        self.db.commit()
        return entry

    def get_recent(self, limit: int = 50) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_entity(self, entity_type: str, entity_id: int, limit: int = 20) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
