"""
Auth Controller — JWT login endpoint.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.providers.jwt_provider import create_access_token
from application.repositories.user_repository import UserRepository
from application.exception.custom_exception import UnauthorizedException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    summary="Login and obtain JWT access token",
    response_description="Bearer access token",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate with username + password (form-data).
    Returns a JWT Bearer token valid for the configured expiry period.

    **Sample Request (curl):**
    ```
    curl -X POST /auth/login \\
      -d "username=admin&password=secret"
    ```
    """
    repo = UserRepository(db)
    user = repo.authenticate(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException(detail="Incorrect username or password.")

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
    }
