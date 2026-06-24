"""
Notification Controller — per-user notification queue + system broadcast history.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from application.core.redis import get_redis
from application.controllers.api.dependencies import get_current_user
from application.services.notification_service import NotificationService
from application.src.models.user_model import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class MarkReadRequest(BaseModel):
    notification_id: str


@router.get(
    "/me",
    summary="Get my notifications",
)
async def get_my_notifications(
    limit: int = 20,
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    """Returns the latest notifications for the authenticated user (newest first)."""
    svc = NotificationService(redis)
    notifications = await svc.get_user_notifications(current_user.id, limit=limit)
    return {"notifications": notifications, "count": len(notifications)}


@router.put(
    "/me/read",
    summary="Mark a notification as read",
)
async def mark_notification_read(
    body: MarkReadRequest,
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    svc = NotificationService(redis)
    await svc.mark_read(current_user.id, body.notification_id)
    return {"detail": "Marked as read."}


@router.put(
    "/me/read-all",
    summary="Mark all notifications as read",
)
async def mark_all_read(
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    svc = NotificationService(redis)
    await svc.mark_all_read(current_user.id)
    return {"detail": "All notifications marked as read."}


@router.get(
    "/system",
    summary="Get recent system broadcast notifications",
)
async def get_system_notifications(
    limit: int = 10,
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """Returns the most recent system-wide broadcast notifications."""
    svc = NotificationService(redis)
    notifications = await svc.get_system_history(limit=limit)
    return {"notifications": notifications, "count": len(notifications)}
