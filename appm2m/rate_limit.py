import os

import redis.asyncio as redis
from fastapi import HTTPException, Request, Response, status
from redis.exceptions import RedisError

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

LOGIN_LIMIT = 5  # attempts
LOGIN_WINDOW = 60  # seconds


async def connect_redis() -> redis.Redis | None:
    """Called once by the lifespan. Returns None if Redis isn't reachable."""
    client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    try:
        await client.ping()
    except RedisError as error:
        print(f"[STARTUP] WARNING: Redis not reachable at {REDIS_URL} ({error}) - login is disabled")
        await client.aclose()
        return None
    print(f"[STARTUP] connected to Redis at {REDIS_URL}")
    return client


def limiter(name: str, limit: int, window: int):
    """Dependency factory: allow `limit` requests per `window` seconds per IP."""

    async def check(request: Request, response: Response) -> None:
        r: redis.Redis | None = getattr(request.app.state, "redis", None)
        if r is None:
            # fail closed: no Redis = no way to count attempts = no login
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiter unavailable (Redis is not running)",
            )

        key = f"rate:{name}:{request.client.host}"
        try:
            count = await r.incr(key)
            if count == 1:
                await r.expire(key, window)
            ttl = await r.ttl(key)
        except RedisError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiter unavailable (lost connection to Redis)",
            )

        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts ({limit} per {window} seconds). Try again in {ttl} seconds.",
                headers={"Retry-After": str(ttl)},
            )

        # let the client see how many attempts are left
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - count)

    return check


login_limiter = limiter("login", LOGIN_LIMIT, LOGIN_WINDOW)
