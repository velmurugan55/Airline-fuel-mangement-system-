"""
JWT Provider — token creation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from application.config import settings
from application.exception.custom_exception import UnauthorizedException

import logging

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Raises UnauthorizedException if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode error: %s", exc)
        raise UnauthorizedException(detail="Could not validate credentials.")


def get_token_subject(token: str) -> str:
    """
    Extract the 'sub' claim (username) from the token.
    """
    payload = decode_access_token(token)
    subject: Optional[str] = payload.get("sub")
    if subject is None:
        raise UnauthorizedException(detail="Token subject missing.")
    return subject
