"""Redis rate limiting for public widget API keys."""

from __future__ import annotations

from redis.asyncio import Redis, from_url

from app.core.config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = from_url(settings.redis_url, decode_responses=True)
    return _redis


async def check_rate_limit(*, api_key: str, ip: str, limit_rpm: int) -> tuple[bool, int]:
    """
    Returns (allowed, retry_after_seconds).
    Tracks per API key and per IP (stricter of the two).
    """
    client = await get_redis()
    limit = max(1, limit_rpm)
    key_bucket = f"rl:key:{api_key}"
    ip_bucket = f"rl:ip:{ip}"

    pipe = client.pipeline()
    pipe.incr(key_bucket)
    pipe.expire(key_bucket, 60, nx=True)
    pipe.incr(ip_bucket)
    pipe.expire(ip_bucket, 60, nx=True)
    key_count, _, ip_count, _ = await pipe.execute()

    # Global IP ceiling = 2x tenant rpm to stop one IP hammering many keys lightly
    ip_limit = limit * 2
    if int(key_count) > limit or int(ip_count) > ip_limit:
        ttl = await client.ttl(key_bucket if int(key_count) > limit else ip_bucket)
        return False, max(1, int(ttl) if ttl and ttl > 0 else 60)
    return True, 0
