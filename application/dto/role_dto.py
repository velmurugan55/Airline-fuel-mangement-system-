"""
Role Data Transfer Objects.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class RoleCreateDTO(BaseModel):
    role_name:   str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    is_active:   bool = True


class RoleUpdateDTO(BaseModel):
    role_name:   Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    is_active:   Optional[bool] = None


class RoleResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:          int
    role_name:   str
    description: Optional[str] = None
    is_active:   bool
    created_at:  Optional[datetime] = None
    updated_at:  Optional[datetime] = None


class RoleListResponseDTO(BaseModel):
    total: int
    data:  List[RoleResponseDTO]
