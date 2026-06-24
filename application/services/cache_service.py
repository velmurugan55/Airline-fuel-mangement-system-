"""
CacheService — typed wrapper around Redis get/set/delete.
All methods fail-open: a None redis client or any Redis error is silently
swallowed so the primary DB path is never interrupted.
"""

import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis

from application.core.cache import CacheTTL

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis: Optional[Redis]):
        self._r = redis

    # ── primitives ─────────────────────────────────────────────────────────────

    async def get(self, key: str) -> Optional[Any]:
        if not self._r:
            return None
        try:
            raw = await self._r.get(key)
            return json.loads(raw) if raw is not None else None
        except Exception as exc:
            logger.debug("cache.get(%s) error: %s", key, exc)
            return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        if not self._r:
            return False
        try:
            await self._r.set(key, json.dumps(value, default=str), ex=ttl)
            return True
        except Exception as exc:
            logger.debug("cache.set(%s) error: %s", key, exc)
            return False

    async def delete(self, *keys: str) -> int:
        if not self._r or not keys:
            return 0
        try:
            return await self._r.delete(*keys)
        except Exception as exc:
            logger.debug("cache.delete error: %s", exc)
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        if not self._r:
            return 0
        try:
            count = 0
            async for key in self._r.scan_iter(match=pattern, count=100):
                await self._r.delete(key)
                count += 1
            return count
        except Exception as exc:
            logger.debug("cache.delete_pattern(%s) error: %s", pattern, exc)
            return 0

    async def delete_many_patterns(self, patterns: list[str]) -> None:
        for p in patterns:
            if p.endswith("*") or "*" in p:
                await self.delete_pattern(p)
            else:
                await self.delete(p)

    # ── domain helpers ─────────────────────────────────────────────────────────

    async def get_airlines(self) -> Optional[Any]:
        from application.core.cache import CacheKey
        return await self.get(CacheKey.AIRLINE_LIST)

    async def set_airlines(self, data: Any) -> None:
        from application.core.cache import CacheKey
        await self.set(CacheKey.AIRLINE_LIST, data, CacheTTL.AIRLINE_LIST)

    async def get_vendors(self) -> Optional[Any]:
        from application.core.cache import CacheKey
        return await self.get(CacheKey.VENDOR_LIST)

    async def set_vendors(self, data: Any) -> None:
        from application.core.cache import CacheKey
        await self.set(CacheKey.VENDOR_LIST, data, CacheTTL.VENDOR_LIST)

    async def get_fuel_prices(self) -> Optional[Any]:
        from application.core.cache import CacheKey
        return await self.get(CacheKey.FUEL_PRICE_LIST)

    async def set_fuel_prices(self, data: Any) -> None:
        from application.core.cache import CacheKey
        await self.set(CacheKey.FUEL_PRICE_LIST, data, CacheTTL.FUEL_PRICE_LIST)

    async def get_transactions(self) -> Optional[Any]:
        from application.core.cache import CacheKey
        return await self.get(CacheKey.TRANSACTION_LIST)

    async def set_transactions(self, data: Any) -> None:
        from application.core.cache import CacheKey
        await self.set(CacheKey.TRANSACTION_LIST, data, CacheTTL.TRANSACTION_LIST)

    async def get_dashboard(self, filters: Optional[dict] = None) -> Optional[Any]:
        from application.core.cache import CacheKey
        return await self.get(CacheKey.dashboard(filters))

    async def set_dashboard(self, data: Any, filters: Optional[dict] = None) -> None:
        from application.core.cache import CacheKey
        await self.set(CacheKey.dashboard(filters), data, CacheTTL.DASHBOARD)

    async def get_invoice_report(self, filters: Optional[dict] = None) -> Optional[Any]:
        from application.core.cache import CacheKey
        return await self.get(CacheKey.invoice_report(filters))

    async def set_invoice_report(self, data: Any, filters: Optional[dict] = None) -> None:
        from application.core.cache import CacheKey
        await self.set(CacheKey.invoice_report(filters), data, CacheTTL.INVOICE_REPORT)
