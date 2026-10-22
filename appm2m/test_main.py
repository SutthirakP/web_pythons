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
