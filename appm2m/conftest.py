"""Shared test setup. pytest loads this file automatically before test_main.py.

It points the app at a throwaway database so tests never touch the real
appm2m/catalog.db or appm2m/uploads/, and at Redis database 15 (the app uses 0),
so the login counters the tests create never mix with the real ones.

Redis must be running for the tests:  docker start my-radis
"""

import os
import tempfile
from pathlib import Path

# Must happen BEFORE appm2m.database is imported: the engine reads it at import time.
TEST_DIR = Path(tempfile.mkdtemp(prefix="catalog-test-"))
os.environ["CATALOG_DB"] = str(TEST_DIR / "test_catalog.db")
TEST_REDIS_URL = "redis://localhost:6379/15"
os.environ["REDIS_URL"] = TEST_REDIS_URL

import pytest  # noqa: E402
import redis  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from appm2m import upload  # noqa: E402
from appm2m.database import Base, engine  # noqa: E402
from appm2m.main import app  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A client with the lifespan running and an empty database.

    `with TestClient(app)` is what triggers the lifespan (startup before the
    block, shutdown after it) - exactly like starting and stopping uvicorn.
    """
    Base.metadata.drop_all(bind=engine)  # fresh start; lifespan's create_all rebuilds the tables
    try:
        with redis.Redis.from_url(TEST_REDIS_URL, socket_connect_timeout=2) as r:
            r.flushdb()  # reset login counters - only touches test database 15
    except redis.RedisError:
        pytest.fail("Redis is not running - start it with: docker start my-radis")
    monkeypatch.setattr(upload, "UPLOAD_DIR", tmp_path)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def redis_db():
    """Direct connection to the test Redis, to look at the counters the app writes."""
    with redis.Redis.from_url(TEST_REDIS_URL, decode_responses=True) as r:
        yield r


@pytest.fixture
def auth_headers(client):
    """Register + log in a test user, return the Authorization header."""
    client.post("/register", json={"username": "tester", "password": "secret"})
    r = client.post("/login", data={"username": "tester", "password": "secret"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
