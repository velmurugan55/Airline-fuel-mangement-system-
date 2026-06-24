"""
TokenService — refresh token lifecycle management using Redis.

Storage model:
  refresh_token:jti:{jti}        → username  (TTL = REFRESH_TOKEN_EXPIRE_DAYS)
  refresh_tokens:user:{username} → set of active JTIs (TTL refreshed on rotate)
"""

import logging
import uuid
from datetime import timedelta
from typing import Optional

from redis.asyncio import Redis

from application.config import settings
from application.core.cache import CacheKey, CacheTTL
from application.providers.jwt_provider import create_access_token

logger = logging.getLogger(__name__)

_TTL = CacheTTL.REFRESH_TOKEN


class TokenService:
    def __init__(self, redis: Optional[Redis]):
        self._r = redis

    # ── store ──────────────────────────────────────────────────────────────────

    async def create_refresh_token(self, username: str, role: str) -> Optional[str]:
        """Generate and store a new refresh token JTI. Returns the opaque JTI string."""
        if not self._r:
            return None
        jti = str(uuid.uuid4())
        try:
            pipe = self._r.pipeline()
            pipe.set(CacheKey.refresh_token_jti(jti), username, ex=_TTL)
            pipe.sadd(CacheKey.user_refresh_tokens(username), jti)
            pipe.expire(CacheKey.user_refresh_tokens(username), _TTL)
            await pipe.execute()
            return jti
        except Exception as exc:
            logger.debug("create_refresh_token error: %s", exc)
            return None

    # ── validate ───────────────────────────────────────────────────────────────

    async def validate_refresh_token(self, jti: str) -> Optional[str]:
        """Returns the username bound to this JTI, or None if invalid/expired."""
        if not self._r:
            return None
        try:
            username = await self._r.get(CacheKey.refresh_token_jti(jti))
            return username
        except Exception as exc:
            logger.debug("validate_refresh_token error: %s", exc)
            return None

    # ── revoke ─────────────────────────────────────────────────────────────────

    async def revoke_refresh_token(self, jti: str) -> None:
        if not self._r:
            return
        try:
            username = await self._r.get(CacheKey.refresh_token_jti(jti))
            pipe = self._r.pipeline()
            pipe.delete(CacheKey.refresh_token_jti(jti))
            if username:
                pipe.srem(CacheKey.user_refresh_tokens(username), jti)
            await pipe.execute()
        except Exception as exc:
            logger.debug("revoke_refresh_token error: %s", exc)

    async def revoke_all_user_tokens(self, username: str) -> None:
        if not self._r:
            return
        try:
            jtis = await self._r.smembers(CacheKey.user_refresh_tokens(username))
            if jtis:
                pipe = self._r.pipeline()
                for jti in jtis:
                    pipe.delete(CacheKey.refresh_token_jti(jti))
                pipe.delete(CacheKey.user_refresh_tokens(username))
                await pipe.execute()
        except Exception as exc:
            logger.debug("revoke_all_user_tokens error: %s", exc)

    # ── rotate ─────────────────────────────────────────────────────────────────

    async def rotate_refresh_token(self, old_jti: str, username: str, role: str) -> Optional[str]:
        """Revoke old JTI and issue a new one atomically."""
        await self.revoke_refresh_token(old_jti)
        return await self.create_refresh_token(username, role)

    # ── issue new access token from refresh JTI ────────────────────────────────

    async def refresh_access_token(self, jti: str, role: str) -> Optional[dict]:
        username = await self.validate_refresh_token(jti)
        if not username:
            return None
        new_access = create_access_token(
            data={"sub": username, "role": role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        new_jti = await self.rotate_refresh_token(jti, username, role)
        return {
            "access_token": new_access,
            "token_type": "bearer",
            "username": username,
            "role": role,
            "refresh_token": new_jti,
        }
