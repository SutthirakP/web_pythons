import json

from fastapi.testclient import TestClient

from appm2m.main import app


# ---------- lifespan ----------


def test_without_with_lifespan_does_not_run():
    # no `with` -> startup never runs -> db_ready is never set -> 503
    client = TestClient(app)
    r = client.get("/products/")
    assert r.status_code == 503
    assert r.json()["detail"] == "Database is not ready"


def test_with_lifespan_connects_database(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["db_ready"] is True
    assert body["started_at"] is not None
    assert body["products"] == 0  # fresh test database


def test_lifespan_shutdown_closes_database():
    with TestClient(app) as client:
        assert client.get("/health").json()["db_ready"] is True
    # leaving the `with` block runs the shutdown part of the lifespan
    assert app.state.db_ready is False


# ---------- products ----------


def test_add_product(client, auth_headers):
    r = client.post(
        "/products/",
        json={"name": "USB Hub", "description": "4-port", "price": 20},
        headers=auth_headers,
    )
    assert r.status_code == 200
    product = r.json()
    assert product["id"] == 1
    assert product["name"] == "USB Hub"
    assert product["description"] == "4-port"
    assert product["price"] == 20.0
    assert product["categories"] == []

    r = client.get("/products/")
    assert [p["name"] for p in r.json()] == ["USB Hub"]


def test_add_product_requires_login(client):
    r = client.post("/products/", json={"name": "USB Hub", "price": 20})
    assert r.status_code == 401
    assert client.get("/products/").json() == [] 


def test_add_product_with_category(client, auth_headers):
    category = client.post("/categories/", json={"name": "Electronics"}, headers=auth_headers).json()

    r = client.post(
        "/products/",
        json={"name": "Webcam", "price": 990, "category_ids": [category["id"]]},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["categories"] == [{"id": category["id"], "name": "Electronics"}]


def test_add_product_unknown_category(client, auth_headers):
    r = client.post(
        "/products/",
        json={"name": "Webcam", "price": 990, "category_ids": [99]},
        headers=auth_headers,
    )
    assert r.status_code == 404
    assert "99" in r.json()["detail"]


def test_add_product_invalid_price(client, auth_headers):
    r = client.post("/products/", json={"name": "Webcam", "price": "cheap"}, headers=auth_headers)
    assert r.status_code == 422  # rejected by the Pydantic schema before our code runs


def test_add_product_with_image(client, auth_headers):
    upload = client.post(
        "/upload",
        files={"file": ("photo.png", b"fake-png-bytes", "image/png")},
        headers=auth_headers,
    )
    assert upload.status_code == 200
    filename = upload.json()["filename"]

    r = client.post(
        "/products/",
        json={"name": "Camera", "price": 4500, "image": filename},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["image"] == filename
    assert client.get(f"/file/{filename}").content == b"fake-png-bytes"


def test_update_product(client, auth_headers):
    product = client.post("/products/", json={"name": "Mouse", "price": 590}, headers=auth_headers).json()

    r = client.put(
        f"/products/{product['id']}",
        json={"name": "Wireless Mouse", "price": 790},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Wireless Mouse"
    assert r.json()["price"] == 790.0


def test_delete_product(client, auth_headers):
    product = client.post("/products/", json={"name": "Mouse", "price": 590}, headers=auth_headers).json()

    r = client.delete(f"/products/{product['id']}", headers=auth_headers)
    assert r.status_code == 200
    assert client.get(f"/products/{product['id']}").status_code == 404


def test_get_missing_product(client):
    r = client.get("/products/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Product not found"}


# ---------- auth ----------


def test_register_duplicate_username(client):
    first = client.post("/register", json={"username": "somchai", "password": "pw"})
    second = client.post("/register", json={"username": "somchai", "password": "pw"})
    assert first.status_code == 200
    assert second.status_code == 409


def test_login_wrong_password(client):
    client.post("/register", json={"username": "somchai", "password": "pw"})
    r = client.post("/login", data={"username": "somchai", "password": "wrong"})
    assert r.status_code == 400


# ---------- login rate limit (Redis) ----------


def login(client, password="pw"):
    return client.post("/login", data={"username": "somchai", "password": password})


def test_login_allows_5_attempts_then_blocks(client):
    client.post("/register", json={"username": "somchai", "password": "pw"})

    for attempt in range(1, 6):
        r = login(client)
        assert r.status_code == 200, f"attempt {attempt} should be allowed"
        assert r.headers["X-RateLimit-Remaining"] == str(5 - attempt)

    r = login(client)  # 6th attempt in the same minute
    assert r.status_code == 429
    assert "Too many login attempts" in r.json()["detail"]
    assert 0 < int(r.headers["Retry-After"]) <= 60


def test_wrong_passwords_count_too(client):
    client.post("/register", json={"username": "somchai", "password": "pw"})

    for _ in range(5):
        assert login(client, password="wrong").status_code == 400

    # even the right password is refused now - stops password guessing
    assert login(client, password="pw").status_code == 429


def test_login_counter_is_stored_in_redis(client, redis_db):
    client.post("/register", json={"username": "somchai", "password": "pw"})
    login(client)
    login(client)

    key = "rate:login:testclient"  # TestClient's fake IP is "testclient"
    assert redis_db.get(key) == "2"
    assert 0 < redis_db.ttl(key) <= 60  # deletes itself after the window


def test_limit_resets_when_redis_key_expires(client, redis_db):
    client.post("/register", json={"username": "somchai", "password": "pw"})
    for _ in range(5):
        login(client)
    assert login(client).status_code == 429

    redis_db.delete("rate:login:testclient")  # same as waiting 60 seconds
    assert login(client).status_code == 200


def test_other_endpoints_are_not_limited(client):
    for _ in range(10):
        assert client.get("/products/").status_code == 200


def test_login_refused_when_redis_is_down(client):
    saved = app.state.redis
    app.state.redis = None  # pretend Redis wasn't reachable at startup
    try:
        r = login(client)
        assert r.status_code == 503
        assert "Redis" in r.json()["detail"]
    finally:
        app.state.redis = saved


def test_health_shows_redis(client):
    assert client.get("/health").json()["redis_ready"] is True


# ---------- CORS: every method except HEAD ----------

ORIGIN = {"Origin": "http://localhost:3000"}


def test_head_foo_works_without_browser(client):
    # no Origin header = not a browser cross-origin call -> CORS doesn't apply
    r = client.head("/foo")
    assert r.status_code == 200
    assert r.headers["X-Foo"] == "hello from HEAD"


def test_head_foo_gets_no_cors_header(client):
    # what the browser sends for fetch(url, {method: "HEAD"}) - no preflight
    r = client.head("/foo", headers=ORIGIN)
    assert r.status_code == 200  # the server still answers...
    assert "access-control-allow-origin" not in r.headers  # ...but the browser will block it


def test_get_foo_gets_cors_header(client):
    r = client.get("/foo", headers=ORIGIN)
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_preflight_rejects_head(client):
    r = client.options("/foo", headers={**ORIGIN, "Access-Control-Request-Method": "HEAD"})
    assert r.status_code == 400
    assert "method" in r.text


def test_preflight_allows_other_methods(client):
    for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
        r = client.options("/foo", headers={**ORIGIN, "Access-Control-Request-Method": method})
        assert r.status_code == 200, method


# ---------- streaming description (SSE) ----------


def read_events(response):
    """Turn a text/event-stream body into a list of (event, data) pairs."""
    events = []
    for block in response.text.strip().split("\n\n"):
        fields = dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)
        events.append((fields.get("event"), fields.get("data")))
    return events


def test_describe_streams_word_by_word(client, auth_headers, monkeypatch):
    from appm2m import streaming
    monkeypatch.setattr(streaming, "WORD_DELAY", 0)
    monkeypatch.setattr(streaming, "THINKING_DELAY", 0)
    product = client.post("/products/", json={"name": "USB Hub", "price": 20}, headers=auth_headers).json()

    r = client.get(f"/products/{product['id']}/describe")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")

    events = read_events(r)
    names = [name for name, _ in events]
    assert names[0] == "start"
    assert names[-1] == "done"
    tokens = [json.loads(data) for name, data in events if name == "token"]
    assert len(tokens) > 10  # many small pieces, not one big answer

    full_text = json.loads(events[-1][1])["text"]
    assert "".join(tokens) == full_text  # the pieces add up to the whole text
    assert "USB Hub" in full_text
    assert "$20.00" in full_text


def test_describe_missing_product_is_404(client):
    r = client.get("/products/999/describe")
    assert r.status_code == 404


# ---------- cookie: remember login status ----------


def register_and_login(client, username="somchai", password="pw", remember=False):
    client.post("/register", json={"username": username, "password": password})
    return client.post(
        "/login",
        data={"username": username, "password": password, "remember": str(remember).lower()},
    )


def test_login_sets_session_cookie(client):
    r = register_and_login(client)
    assert r.status_code == 200

    set_cookie = r.headers["set-cookie"]
    assert set_cookie.startswith("session_id=")
    assert "HttpOnly" in set_cookie  # JavaScript can't read it
    assert "SameSite=lax" in set_cookie
    assert "somchai" not in set_cookie  # only a random key, not the username


def test_me_without_cookie_is_401(client):
    assert client.get("/me").status_code == 401


def test_me_remembers_user_from_cookie(client):
    user_id = register_and_login(client).json()["user"]["id"]

    # no Authorization header - TestClient just sends the cookie back, like a browser
    r = client.get("/me")
    assert r.status_code == 200
    assert r.json() == {"id": user_id, "username": "somchai", "remember": False, "logged_in": True}


def test_cookie_alone_can_add_product(client):
    register_and_login(client)
    r = client.post("/products/", json={"name": "Mouse", "price": 590})  # no Bearer token
    assert r.status_code == 200


def test_session_is_stored_in_redis(client, redis_db):
    user_id = register_and_login(client).json()["user"]["id"]
    session_id = client.cookies["session_id"]

    stored = json.loads(redis_db.get(f"session:{session_id}"))
    assert stored == {"user_id": user_id, "username": "somchai", "remember": False}
    assert 0 < redis_db.ttl(f"session:{session_id}") <= 3600


def test_fake_cookie_is_rejected(client):
    client.cookies.set("session_id", "i-made-this-up")
    assert client.get("/me").status_code == 401
    assert client.post("/products/", json={"name": "Hack", "price": 1}).status_code == 401


def test_logout_forgets_the_cookie(client, redis_db):
    register_and_login(client)
    session_id = client.cookies["session_id"]

    r = client.post("/logout")
    assert r.status_code == 200
    assert 'session_id=""' in r.headers["set-cookie"]  # browser is told to delete it
    assert redis_db.get(f"session:{session_id}") is None  # server forgot it too

    client.cookies.set("session_id", session_id)  # even if someone kept a copy...
    assert client.get("/me").status_code == 401  # ...it no longer works


# ---------- "Remember me" checkbox ----------

WEEK = 7 * 24 * 60 * 60


def test_without_remember_me_is_a_session_cookie(client, redis_db):
    r = register_and_login(client, remember=False)
    set_cookie = r.headers["set-cookie"]
    # no Max-Age / Expires = session cookie: the browser deletes it when it closes
    assert "Max-Age" not in set_cookie
    assert "expires" not in set_cookie.lower()
    assert redis_db.ttl(f"session:{client.cookies['session_id']}") <= 3600


def test_with_remember_me_cookie_lasts_7_days(client, redis_db):
    r = register_and_login(client, remember=True)
    assert f"Max-Age={WEEK}" in r.headers["set-cookie"]
    assert 3600 < redis_db.ttl(f"session:{client.cookies['session_id']}") <= WEEK
    assert client.get("/me").json()["remember"] is True


def test_remember_defaults_to_false(client):
    # /docs and old clients don't send the field at all
    client.post("/register", json={"username": "somchai", "password": "pw"})
    r = client.post("/login", data={"username": "somchai", "password": "pw"})
    assert r.status_code == 200
    assert r.json()["user"]["remember"] is False
    assert "Max-Age" not in r.headers["set-cookie"]


# ---------- Redis down at startup, back later ----------


def test_login_recovers_when_redis_comes_back(client):
    import redis.asyncio as aioredis

    client.post("/register", json={"username": "somchai", "password": "pw"})
    working = app.state.redis

    # Redis "down": point at a port where nothing is listening
    app.state.redis = aioredis.from_url("redis://localhost:6399/15", socket_connect_timeout=1)
    try:
        r = client.post("/login", data={"username": "somchai", "password": "pw"})
        assert r.status_code == 503
        assert "docker start my-radis" in r.json()["detail"]
        assert client.get("/health").json()["redis_ready"] is False
    finally:
        app.state.redis = working  # Redis "back up" - same running server, no restart

    assert client.get("/health").json()["redis_ready"] is True
    assert client.post("/login", data={"username": "somchai", "password": "pw"}).status_code == 200


def test_connect_redis_keeps_client_even_if_down(monkeypatch):
    import asyncio

    from appm2m import rate_limit

    monkeypatch.setattr(rate_limit, "REDIS_URL", "redis://localhost:6399/15")
    client = asyncio.run(rate_limit.connect_redis())
    assert client is not None  # not None -> it will retry on later requests
    assert asyncio.run(rate_limit.redis_is_up(client)) is False
