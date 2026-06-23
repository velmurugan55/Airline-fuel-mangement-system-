"""
User Domain Entity.
"""

from pydantic import BaseModel, ConfigDict
from application.src.models.user_model import UserRole


class UserEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
