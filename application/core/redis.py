"""
Redis async connection pool. All Redis operations across the app use this
single pool — never create ad-hoc connections.

Fail-open design: if Redis is unavailable, callers must handle None or catch
ConnectionError so the primary DB path is never blocked.
"""

import logging
from typing import Optional, AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from application.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[ConnectionPool] = None


async def init_redis_pool() -> None:
    global _pool
    kwargs: dict = {
        "host": settings.REDIS_HOST,
        "port": settings.REDIS_PORT,
        "db": settings.REDIS_DB,
        "decode_responses": True,
        "max_connections": 20,
        "socket_connect_timeout": 2,
        "socket_timeout": 2,
        "retry_on_timeout": False,
    }
    if settings.REDIS_PASSWORD:
        kwargs["password"] = settings.REDIS_PASSWORD
    try:
        _pool = ConnectionPool(**kwargs)
        client = aioredis.Redis(connection_pool=_pool)
        await client.ping()
        await client.aclose()
        logger.info("Redis pool initialised  %s:%s db=%s", settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)
    except Exception as exc:
        logger.warning("Redis unavailable at startup — caching disabled. %s", exc)
        _pool = None


async def close_redis_pool() -> None:
    global _pool
    if _pool:
        await _pool.aclose()
        _pool = None
        logger.info("Redis pool closed.")


def get_redis_client() -> Optional[aioredis.Redis]:
    if _pool is None:
        return None
    return aioredis.Redis(connection_pool=_pool)


async def get_redis() -> AsyncGenerator[Optional[aioredis.Redis], None]:
    """FastAPI dependency — yields a Redis client or None when unavailable."""
    client = get_redis_client()
    try:
        yield client
    finally:
        if client:
            await client.aclose()


async def redis_health() -> dict:
    client = get_redis_client()
    if client is None:
        return {"status": "unavailable"}
    try:
        pong = await client.ping()
        info = await client.info("server")
        await client.aclose()
        return {
            "status": "healthy" if pong else "degraded",
            "version": info.get("redis_version", "unknown"),
        }
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
