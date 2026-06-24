"""
Sliding-window rate limiter using Redis sorted sets.

Each request adds (timestamp, timestamp) to a sorted set keyed by
rate_limit:{kind}:{identifier}.  Old entries outside the window are pruned
before the count is checked.  If over the limit, raise HTTP 429.
"""

import logging
import time
from typing import Optional

from fastapi import HTTPException, status
from redis.asyncio import Redis

from application.core.cache import CacheKey

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, redis: Optional[Redis]):
        self._r = redis

    async def check(
        self,
        kind: str,
        identifier: str,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        """Raise HTTP 429 if the caller has exceeded the rate limit."""
        if not self._r:
            return

        key = CacheKey.rate_limit(kind, identifier)
        now = time.time()
        window_start = now - window_seconds

        try:
            pipe = self._r.pipeline()
            pipe.zremrangebyscore(key, "-inf", window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds + 1)
            results = await pipe.execute()
            count = results[2]
        except Exception as exc:
            logger.debug("rate_limiter.check error: %s", exc)
            return

        if count > max_requests:
            retry_after = int(window_seconds)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

    async def check_login(self, identifier: str) -> None:
        """5 login attempts per minute per IP/username."""
        await self.check("login", identifier, max_requests=5, window_seconds=60)

    async def check_api(self, identifier: str) -> None:
        """200 API calls per minute per user."""
        await self.check("api", identifier, max_requests=200, window_seconds=60)
