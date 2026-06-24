"""
NotificationService — per-user notification queues + system broadcast.

Per-user queue:
  notifications:user:{user_id}           → Redis List (newest first, capped at 50)
  notifications:user:{user_id}:read      → Redis Set  (notification IDs read)

System broadcast:
  notifications:system                   → Pub/Sub channel
  notifications:system:history           → Redis List (last 20 broadcasts)
"""

import json
import logging
import time
from typing import Optional

from redis.asyncio import Redis

from application.core.cache import CacheKey

logger = logging.getLogger(__name__)

_MAX_USER_NOTIFICATIONS = 50
_MAX_SYSTEM_HISTORY = 20


def _make_notification(message: str, kind: str = "info", entity_type: str = "", entity_id: int = 0) -> dict:
    return {
        "id": str(int(time.time() * 1000)),
        "message": message,
        "kind": kind,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "ts": int(time.time()),
    }


class NotificationService:
    def __init__(self, redis: Optional[Redis]):
        self._r = redis

    # ── user queue ─────────────────────────────────────────────────────────────

    async def push_user(self, user_id: int, message: str, kind: str = "info",
                        entity_type: str = "", entity_id: int = 0) -> None:
        if not self._r:
            return
        notif = _make_notification(message, kind, entity_type, entity_id)
        key = CacheKey.user_notifications(user_id)
        try:
            pipe = self._r.pipeline()
            pipe.lpush(key, json.dumps(notif))
            pipe.ltrim(key, 0, _MAX_USER_NOTIFICATIONS - 1)
            await pipe.execute()
        except Exception as exc:
            logger.debug("push_user notification error: %s", exc)

    async def get_user_notifications(self, user_id: int, limit: int = 20) -> list:
        if not self._r:
            return []
        key = CacheKey.user_notifications(user_id)
        read_key = CacheKey.user_notifications_read(user_id)
        try:
            raw_list = await self._r.lrange(key, 0, limit - 1)
            read_ids = await self._r.smembers(read_key)
            result = []
            for raw in raw_list:
                notif = json.loads(raw)
                notif["read"] = notif["id"] in read_ids
                result.append(notif)
            return result
        except Exception as exc:
            logger.debug("get_user_notifications error: %s", exc)
            return []

    async def mark_read(self, user_id: int, notification_id: str) -> None:
        if not self._r:
            return
        try:
            await self._r.sadd(CacheKey.user_notifications_read(user_id), notification_id)
            await self._r.expire(CacheKey.user_notifications_read(user_id), 60 * 60 * 24 * 30)
        except Exception as exc:
            logger.debug("mark_read error: %s", exc)

    async def mark_all_read(self, user_id: int) -> None:
        if not self._r:
            return
        notifications = await self.get_user_notifications(user_id, limit=_MAX_USER_NOTIFICATIONS)
        for n in notifications:
            await self.mark_read(user_id, n["id"])

    # ── system broadcast ───────────────────────────────────────────────────────

    async def broadcast_system(self, message: str, kind: str = "info") -> None:
        if not self._r:
            return
        notif = _make_notification(message, kind)
        payload = json.dumps(notif)
        try:
            pipe = self._r.pipeline()
            pipe.publish(CacheKey.SYSTEM_NOTIFICATIONS_CHANNEL, payload)
            pipe.lpush(CacheKey.SYSTEM_NOTIFICATIONS_HISTORY, payload)
            pipe.ltrim(CacheKey.SYSTEM_NOTIFICATIONS_HISTORY, 0, _MAX_SYSTEM_HISTORY - 1)
            await pipe.execute()
        except Exception as exc:
            logger.debug("broadcast_system error: %s", exc)

    async def get_system_history(self, limit: int = 10) -> list:
        if not self._r:
            return []
        try:
            raw_list = await self._r.lrange(CacheKey.SYSTEM_NOTIFICATIONS_HISTORY, 0, limit - 1)
            return [json.loads(r) for r in raw_list]
        except Exception as exc:
            logger.debug("get_system_history error: %s", exc)
            return []

    # ── domain helpers ─────────────────────────────────────────────────────────

    async def notify_new_transaction(self, user_id: int, invoice_no: str, amount: float) -> None:
        await self.push_user(
            user_id,
            f"New transaction recorded: {invoice_no} — ${amount:,.2f}",
            kind="success",
            entity_type="transaction",
        )
        await self.broadcast_system(
            f"New fuel transaction: {invoice_no}",
            kind="info",
        )

    async def notify_price_update(self, vendor_name: str, new_price: float) -> None:
        await self.broadcast_system(
            f"Fuel price updated for {vendor_name}: ${new_price:.4f}/L",
            kind="warning",
        )
