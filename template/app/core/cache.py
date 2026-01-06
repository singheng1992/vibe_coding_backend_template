"""缓存模块。

提供 Redis 缓存连接和操作。
"""
from typing import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

# Redis 连接池
_redis_pool: ConnectionPool | None = None


def get_redis_pool() -> ConnectionPool:
    """获取 Redis 连接池。

    Returns:
        Redis 连接池。
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return _redis_pool


async def get_redis() -> AsyncGenerator[Redis, None]:
    """获取 Redis 客户端。

    Yields:
        Redis 客户端。
    """
    pool = get_redis_pool()
    async with Redis(connection_pool=pool) as redis:
        yield redis


async def close_redis() -> None:
    """关闭 Redis 连接池。"""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
