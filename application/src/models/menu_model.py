"""
Menu SQLAlchemy Model — supports parent-child hierarchy for nested sidebar groups.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from application.providers.database import Base


class Menu(Base):
    __tablename__ = "menus"

    id             = Column(Integer, primary_key=True, index=True)
    menu_name      = Column(String(100), nullable=False)
    menu_code      = Column(String(50), unique=True, nullable=False, index=True)
    parent_menu_id = Column(Integer, ForeignKey("menus.id"), nullable=True)
    route_path     = Column(String(255), nullable=True)
    icon           = Column(String(100), nullable=True)
    display_order  = Column(Integer, default=0, nullable=False)
    is_active      = Column(Boolean, default=True, nullable=False)

    # Self-referential relationship for parent-child hierarchy
    children    = relationship("Menu", backref=backref("parent", remote_side=[id]), lazy="select")
    permissions = relationship("RoleMenuPermission", back_populates="menu", cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<Menu id={self.id} code={self.menu_code}>"
