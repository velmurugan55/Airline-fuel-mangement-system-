"""
Auth Controller — JWT login, refresh, logout + sidebar permissions in login response.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from application.providers.database import get_db
from application.providers.jwt_provider import create_access_token
from application.repositories.user_repository import UserRepository
from application.repositories.permission_repository import PermissionRepository
from application.exception.custom_exception import UnauthorizedException
from application.core.redis import get_redis
from application.services.rate_limiter import RateLimiter
from application.services.token_service import TokenService
from application.controllers.api.dependencies import get_current_user
from application.src.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post(
    "/login",
    summary="Login — returns JWT + sidebar permissions",
)
async def login(
    request:   Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:        Session = Depends(get_db),
    redis      = Depends(get_redis),
):
    """
    Authenticate with username + password (form-data).
    Returns:
    - `access_token` (JWT)
    - `refresh_token` (opaque JTI stored in Redis)
    - `permissions` — flat dict keyed by menu_code with 8 boolean flags
    - `menus` — ordered list of menus the user can view (used to build sidebar)
    """
    rate_limiter = RateLimiter(redis)
    client_ip = request.client.host if request.client else "unknown"
    await rate_limiter.check_login(f"{client_ip}:{form_data.username}")

    repo = UserRepository(db)
    user = repo.authenticate(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException(detail="Incorrect username or password.")

    token = create_access_token(data={"sub": user.username, "role": user.role})
    token_svc = TokenService(redis)
    refresh_jti = await token_svc.create_refresh_token(user.username, str(user.role.value))

    # Build sidebar & permission payload
    permissions_data: dict = {}
    menus_data: list = []
    role_name: str = str(user.role.value)

    if user.role_id is not None:
        perm_repo = PermissionRepository(db)
        payload = perm_repo.build_sidebar_payload(user.role_id)
        menus_data = [m.model_dump() for m in payload["menus"]]
        permissions_data = {k: v.model_dump() for k, v in payload["permissions"].items()}
        if user.role_entity:
            role_name = user.role_entity.role_name

    return {
        "access_token":  token,
        "token_type":    "bearer",
        "username":      user.username,
        "role":          str(user.role.value),
        "role_id":       user.role_id,
        "role_name":     role_name,
        "refresh_token": refresh_jti,
        "permissions":   permissions_data,
        "menus":         menus_data,
    }


@router.post("/refresh", summary="Rotate refresh token and get new access token")
async def refresh_token(
    body:  RefreshRequest,
    db:    Session = Depends(get_db),
    redis  = Depends(get_redis),
):
    token_svc = TokenService(redis)
    username = await token_svc.validate_refresh_token(body.refresh_token)
    if not username:
        raise UnauthorizedException(detail="Invalid or expired refresh token.")
    repo = UserRepository(db)
    user = repo.get_by_username(username)
    if not user:
        raise UnauthorizedException(detail="User not found.")
    result = await token_svc.refresh_access_token(body.refresh_token, str(user.role.value))
    if not result:
        raise UnauthorizedException(detail="Could not refresh token.")
    return result


@router.post("/logout", summary="Revoke the current refresh token")
async def logout(
    body:  RefreshRequest,
    redis  = Depends(get_redis),
    _:     User = Depends(get_current_user),
):
    await TokenService(redis).revoke_refresh_token(body.refresh_token)
    return {"detail": "Logged out successfully."}


@router.post("/logout-all", summary="Revoke all refresh tokens for the current user")
async def logout_all(
    redis        = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    await TokenService(redis).revoke_all_user_tokens(current_user.username)
    return {"detail": "Logged out from all devices."}
