"""
Permission Guard — FastAPI dependency factory for button/route level RBAC.

Usage in a controller:
    @router.post("/transactions", dependencies=[Depends(require_permission("transactions", "can_create"))])
    async def create_transaction(...):
        ...

Or inline:
    @router.delete("/airlines/{id}")
    async def delete_airline(
        _=Depends(require_permission("airlines", "can_delete")),
        ...
    ):
        ...

Legacy users (role_id is None) fall back to a simple admin-wins check.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.repositories.permission_repository import PermissionRepository
from application.exception.custom_exception import ForbiddenException
from application.src.models.user_model import User

VALID_ACTIONS = {
    "can_view", "can_create", "can_edit", "can_delete",
    "can_download", "can_approve", "can_export", "can_print",
}


def require_permission(menu_code: str, action: str = "can_view"):
    """
    Returns a FastAPI dependency that enforces the given action on the given menu.
    Raises HTTP 403 if the user's role does not have the requested permission.
    """
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid permission action: {action}. Must be one of {VALID_ACTIONS}")

    async def _guard(
        current_user: User    = Depends(get_current_user),
        db:           Session = Depends(get_db),
    ) -> User:
        # Super-admin bypass: legacy admin role always passes
        if str(current_user.role.value) == "admin" and current_user.role_id is None:
            return current_user

        if current_user.role_id is None:
            raise ForbiddenException(f"No role assigned. Cannot access '{menu_code}'.")

        perm_repo = PermissionRepository(db)
        perm = perm_repo.get_by_menu_code(current_user.role_id, menu_code)

        if perm is None or not getattr(perm, action, False):
            raise ForbiddenException(
                f"Your role does not have '{action}' permission on '{menu_code}'."
            )
        return current_user

    return _guard
