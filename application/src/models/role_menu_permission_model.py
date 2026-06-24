"""
RoleMenuPermission SQLAlchemy Model — 8-action RBAC permission per role per menu.
"""

from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from application.providers.database import Base


class RoleMenuPermission(Base):
    __tablename__ = "role_menu_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "menu_id", name="uq_role_menu"),
    )

    id           = Column(Integer, primary_key=True, index=True)
    role_id      = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_id      = Column(Integer, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True)

    can_view     = Column(Boolean, default=False, nullable=False)
    can_create   = Column(Boolean, default=False, nullable=False)
    can_edit     = Column(Boolean, default=False, nullable=False)
    can_delete   = Column(Boolean, default=False, nullable=False)
    can_download = Column(Boolean, default=False, nullable=False)
    can_approve  = Column(Boolean, default=False, nullable=False)
    can_export   = Column(Boolean, default=False, nullable=False)
    can_print    = Column(Boolean, default=False, nullable=False)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    menu = relationship("Menu", back_populates="permissions")

    def as_dict(self) -> dict:
        return {
            "can_view":     self.can_view,
            "can_create":   self.can_create,
            "can_edit":     self.can_edit,
            "can_delete":   self.can_delete,
            "can_download": self.can_download,
            "can_approve":  self.can_approve,
            "can_export":   self.can_export,
            "can_print":    self.can_print,
        }

    def __repr__(self) -> str:
        return f"<RoleMenuPermission role={self.role_id} menu={self.menu_id}>"
