"""
Menu Repository — DB operations for the Menu model.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from application.src.models.menu_model import Menu
from application.dto.menu_dto import MenuCreateDTO, MenuUpdateDTO


class MenuRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, menu_id: int) -> Optional[Menu]:
        return self.db.query(Menu).filter(Menu.id == menu_id).first()

    def get_by_code(self, menu_code: str) -> Optional[Menu]:
        return self.db.query(Menu).filter(Menu.menu_code == menu_code).first()

    def get_all(self) -> List[Menu]:
        return self.db.query(Menu).order_by(Menu.display_order, Menu.id).all()

    def get_top_level(self) -> List[Menu]:
        return (
            self.db.query(Menu)
            .filter(Menu.parent_menu_id == None, Menu.is_active == True)
            .order_by(Menu.display_order)
            .all()
        )

    def create(self, dto: MenuCreateDTO) -> Menu:
        menu = Menu(**dto.model_dump())
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        return menu

    def update(self, menu: Menu, dto: MenuUpdateDTO) -> Menu:
        for field, value in dto.model_dump(exclude_none=True).items():
            setattr(menu, field, value)
        self.db.commit()
        self.db.refresh(menu)
        return menu

    def delete(self, menu: Menu) -> None:
        self.db.delete(menu)
        self.db.commit()
