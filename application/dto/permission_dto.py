"""
Permission Data Transfer Objects.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict


class PermissionSetDTO(BaseModel):
    can_view:     bool = False
    can_create:   bool = False
    can_edit:     bool = False
    can_delete:   bool = False
    can_download: bool = False
    can_approve:  bool = False
    can_export:   bool = False
    can_print:    bool = False


class RoleMenuPermissionUpdateDTO(BaseModel):
    """Used to bulk-assign all permissions for a role at once."""
    permissions: List["MenuPermissionEntryDTO"]


class MenuPermissionEntryDTO(BaseModel):
    menu_id:      int
    can_view:     bool = False
    can_create:   bool = False
    can_edit:     bool = False
    can_delete:   bool = False
    can_download: bool = False
    can_approve:  bool = False
    can_export:   bool = False
    can_print:    bool = False


RoleMenuPermissionUpdateDTO.model_rebuild()


class PermissionResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:           int
    role_id:      int
    menu_id:      int
    can_view:     bool
    can_create:   bool
    can_edit:     bool
    can_delete:   bool
    can_download: bool
    can_approve:  bool
    can_export:   bool
    can_print:    bool


class SidebarMenuDTO(BaseModel):
    """One menu entry as returned in the login response sidebar payload."""
    menu_id:       int
    menu_name:     str
    menu_code:     str
    parent_menu_id: Optional[int] = None
    route_path:    Optional[str] = None
    icon:          Optional[str] = None
    display_order: int
    can_view:      bool
    can_create:    bool
    can_edit:      bool
    can_delete:    bool
    can_download:  bool
    can_approve:   bool
    can_export:    bool
    can_print:     bool
    children:      List["SidebarMenuDTO"] = []


SidebarMenuDTO.model_rebuild()


class UserPermissionsResponseDTO(BaseModel):
    """Full permission payload returned at login time."""
    role_id:     Optional[int]
    role_name:   Optional[str]
    menus:       List[SidebarMenuDTO] = []
    permissions: Dict[str, PermissionSetDTO] = {}
