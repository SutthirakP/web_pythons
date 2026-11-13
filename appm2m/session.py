"""Cookie login sessions (homework: remember the user ID / login status in a cookie).

Same idea as cookie/main.py, but the session table lives in Redis instead of a
Python dict, so logins survive a server restart (and `--reload`).

    browser cookie:   session_id=<random 43 chars>          (HttpOnly)
    Redis:            session:<random> -> {"user_id": 1, "username": "admin", "remember": true}

    Remember me ticked:     cookie Max-Age 7 days, Redis TTL 7 days
    Remember me not ticked: cookie has no Max-Age (gone when the browser closes), Redis TTL 1 hour

The cookie only holds a random key - never the user ID or password itself - so
nobody can log in as someone else by editing their cookie.
"""

import json
import secrets

import redis.asyncio as redis
from redis.exceptions import RedisError

SESSION_COOKIE = "session_id"

# "Remember me" NOT ticked -> session cookie (no Max-Age): the browser drops it when
# it closes. The Redis copy still expires after an hour in case the browser never closes.
SESSION_SECONDS = 60 * 60
# "Remember me" ticked -> persistent cookie: Max-Age and Redis TTL both 7 days.
REMEMBER_SECONDS = 7 * 24 * 60 * 60


def session_key(session_id: str) -> str:
    return f"session:{session_id}"


async def create_session(r: redis.Redis, user_id: int, username: str, remember: bool) -> str:
    session_id = secrets.token_urlsafe(32)
    data = json.dumps({"user_id": user_id, "username": username, "remember": remember})
    ttl = REMEMBER_SECONDS if remember else SESSION_SECONDS
    await r.set(session_key(session_id), data, ex=ttl)
    return session_id


async def read_session(r: redis.Redis | None, session_id: str | None) -> dict | None:
    if r is None or not session_id:
        return None
    try:
        data = await r.get(session_key(session_id))
    except RedisError:
        return None  # Redis down -> treat as logged out instead of crashing
    return json.loads(data) if data else None


async def delete_session(r: redis.Redis | None, session_id: str | None) -> None:
    if r is not None and session_id:
        try:
            await r.delete(session_key(session_id))
        except RedisError:
            pass  # Redis down - the cookie is still deleted, and the key expires on its own
