"""
Menu Data Transfer Objects.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class MenuCreateDTO(BaseModel):
    menu_name:      str = Field(..., min_length=2, max_length=100)
    menu_code:      str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9_-]+$")
    parent_menu_id: Optional[int] = None
    route_path:     Optional[str] = Field(None, max_length=255)
    icon:           Optional[str] = Field(None, max_length=100)
    display_order:  int = 0
    is_active:      bool = True


class MenuUpdateDTO(BaseModel):
    menu_name:      Optional[str] = Field(None, min_length=2, max_length=100)
    parent_menu_id: Optional[int] = None
    route_path:     Optional[str] = Field(None, max_length=255)
    icon:           Optional[str] = Field(None, max_length=100)
    display_order:  Optional[int] = None
    is_active:      Optional[bool] = None


class MenuResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    menu_name:      str
    menu_code:      str
    parent_menu_id: Optional[int] = None
    route_path:     Optional[str] = None
    icon:           Optional[str] = None
    display_order:  int
    is_active:      bool
    children:       List["MenuResponseDTO"] = []

    @classmethod
    def from_orm_tree(cls, menu) -> "MenuResponseDTO":
        return cls(
            id=menu.id,
            menu_name=menu.menu_name,
            menu_code=menu.menu_code,
            parent_menu_id=menu.parent_menu_id,
            route_path=menu.route_path,
            icon=menu.icon,
            display_order=menu.display_order,
            is_active=menu.is_active,
            children=[cls.from_orm_tree(c) for c in (menu.children or [])],
        )


MenuResponseDTO.model_rebuild()


class MenuListResponseDTO(BaseModel):
    total: int
    data:  List[MenuResponseDTO]
