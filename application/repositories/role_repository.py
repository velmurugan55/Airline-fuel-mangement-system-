"""
Role Repository — DB operations for the Role model.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from application.src.models.role_model import Role
from application.dto.role_dto import RoleCreateDTO, RoleUpdateDTO


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, role_name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.role_name == role_name).first()

    def get_all(self) -> List[Role]:
        return self.db.query(Role).order_by(Role.id).all()

    def get_active(self) -> List[Role]:
        return self.db.query(Role).filter(Role.is_active == True).order_by(Role.id).all()

    def create(self, dto: RoleCreateDTO) -> Role:
        role = Role(
            role_name=dto.role_name,
            description=dto.description,
            is_active=dto.is_active,
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update(self, role: Role, dto: RoleUpdateDTO) -> Role:
        for field, value in dto.model_dump(exclude_none=True).items():
            setattr(role, field, value)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()
