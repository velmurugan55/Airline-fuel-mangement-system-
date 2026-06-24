"""
User Data Transfer Objects — full RBAC user management.
"""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreateDTO(BaseModel):
    username:     str = Field(..., min_length=3, max_length=100)
    first_name:   Optional[str] = Field(None, max_length=100)
    last_name:    Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=30)
    email:        Optional[str] = Field(None, max_length=255)
    password:     str = Field(..., min_length=6)
    role_id:      Optional[int] = None
    role:         Optional[str] = Field(None, description="Legacy role string (admin/operator/viewer)")
    is_active:    bool = True


class UserUpdateDTO(BaseModel):
    first_name:   Optional[str] = Field(None, max_length=100)
    last_name:    Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=30)
    email:        Optional[str] = Field(None, max_length=255)
    role_id:      Optional[int] = None
    role:         Optional[str] = None
    is_active:    Optional[bool] = None


class UserResetPasswordDTO(BaseModel):
    new_password:     str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class RoleInfoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:        int
    role_name: str


class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:           int
    username:     str
    first_name:   Optional[str] = None
    last_name:    Optional[str] = None
    phone_number: Optional[str] = None
    email:        Optional[str] = None
    role:         Optional[str] = None
    role_id:      Optional[int] = None
    role_entity:  Optional[RoleInfoDTO] = None
    is_active:    bool
    created_at:   Optional[datetime] = None
    updated_at:   Optional[datetime] = None

    @property
    def full_name(self) -> str:
        parts = filter(None, [self.first_name, self.last_name])
        return " ".join(parts) or self.username


class UserListResponseDTO(BaseModel):
    total: int
    page:  int
    limit: int
    data:  List[UserResponseDTO]
