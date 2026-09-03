"""Redis 客户端"""
import redis.asyncio as aioredis

from kk.config import config

_redis_client = None


async def get_redis():
    """获取全局共享的异步Redis客户端"""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            config.REDIS_URL, decode_responses=True)
    return _redis_client


async def close_redis():
    """关闭Redis客户端"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
