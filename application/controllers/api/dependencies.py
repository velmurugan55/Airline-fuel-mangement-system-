"""
Shared FastAPI security dependencies.
Provides the current authenticated user via JWT token.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.providers.jwt_provider import get_token_subject
from application.repositories.user_repository import UserRepository
from application.src.models.user_model import User
from application.exception.custom_exception import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extract and validate JWT, return the User ORM object.
    Raises 401 if the token is invalid or user no longer exists.
    """
    username = get_token_subject(token)
    repo = UserRepository(db)
    user = repo.get_by_username(username)
    if not user:
        raise UnauthorizedException(detail="User not found.")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Restrict endpoint to admin role only."""
    if current_user.role != "admin":
        from application.exception.custom_exception import ForbiddenException
        raise ForbiddenException(detail="Admin role required.")
    return current_user
