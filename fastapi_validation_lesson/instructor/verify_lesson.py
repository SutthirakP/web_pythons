"""Instructor checks; uses the lesson dependencies and Python standard library."""
import asyncio
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from main import app


async def request(application, path, payload=None):
    body = b"" if payload is None else json.dumps(payload).encode()
    messages = []

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": "GET" if payload is None else "POST", "scheme": "http",
        "path": path, "raw_path": path.encode(), "query_string": b"",
        "root_path": "", "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 12345), "server": ("testserver", 80),
    }
    await application(scope, receive, send)
    status = next(m["status"] for m in messages if m["type"] == "http.response.start")
    content = b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body")
    return status, content


async def check():
    count = 0
    for path in ("/", "/docs", "/openapi.json"):
        status, _ = await request(app, path)
        assert status == 200, (path, status)
        count += 1

    cases = [
        ({"name": "  ปากกา  ", "price": 25}, 200, None),
        ({"name": "Pen", "price": -10}, 422, "price"),
        ({"name": "Pen", "price": 0}, 422, "price"),
        ({"name": "Pen", "price": "abc"}, 422, "price"),
        ({"name": "Pen", "price": "Infinity"}, 422, "price"),
        ({"name": "Pen", "price": "NaN"}, 422, "price"),
        ({"name": "", "price": 25}, 422, "name"),
        ({"name": "   ", "price": 25}, 422, "name"),
        ({"name": "\t\n", "price": 25}, 422, "name"),
        ({"name": "Pen"}, 422, "price"),
        ({"price": 25}, 422, "name"),
        ({"name": "a" * 100, "price": 25}, 200, None),
        ({"name": "a" * 101, "price": 25}, 422, "name"),
        ({"name": "Pen", "price": 25, "description": "a" * 500}, 200, None),
        ({"name": "Pen", "price": 25, "description": "a" * 501}, 422, "description"),
        ({"name": "Pen", "price": 25, "description": None}, 422, "description"),
        ({"name": "Pen", "price": "25"}, 200, None),
        ({"name": "Pen", "price": 100, "discount_price": 80}, 200, None),
        ({"name": "Pen", "price": 100, "discount_price": 100}, 422, "__model__"),
        ({"name": "Pen", "price": 100, "discount_price": 120}, 422, "__model__"),
        ({"name": "Pen", "price": 100, "discount_price": 0}, 422, "discount_price"),
        ({"name": "Pen", "price": 100, "discount_price": -1}, 422, "discount_price"),
        ({"name": "Pen", "price": 100, "discount_price": "abc"}, 422, "discount_price"),
        ({"name": "Pen", "price": 100, "discount_price": "Infinity"}, 422, "discount_price"),
        ({"name": "Pen", "price": 100, "discount_price": "NaN"}, 422, "discount_price"),
        ({"name": "Pen", "price": 100, "discount_price": None}, 200, None),
        ({"name": "Pen", "price": 100, "discount_price": "80"}, 200, None),
        ({"name": "Pen", "price": "abc", "discount_price": 80}, 422, "price"),
    ]
    for payload, expected, field in cases:
        status, content = await request(app, "/products/validate", payload)
        result = json.loads(content)
        assert status == expected, (payload, status, result)
        if field == "__model__":
            assert any(error["loc"] == ["body"] and "Discount price must be less" in error["msg"] for error in result["detail"]), result
        elif field:
            assert any(error["loc"] == ["body", field] for error in result["detail"]), result
        else:
            assert result["product"]["name"] == payload["name"].strip()
            assert result["product"]["description"] == payload.get("description", "")
            discount = payload.get("discount_price")
            assert result["product"]["discount_price"] == (None if discount is None else float(discount))
        count += 1

    root = ROOT
    blocks = re.findall(r"```python\n(.*?)```", (root / "README.md").read_text(encoding="utf-8"), re.S)
    snapshots = [block for block in blocks if block.startswith("from fastapi import FastAPI\n\n") or block.startswith("from fastapi import FastAPI\nfrom")]
    assert len(snapshots) == 5, len(snapshots)
    assert snapshots[-1].strip() == (root / "main.py").read_text(encoding="utf-8").strip()
    for index, source in enumerate(snapshots):
        namespace = {}
        exec(compile(source, f"README-stage-{index + 1}", "exec"), namespace)
        status, _ = await request(namespace["app"], "/")
        assert status == 200
        if index:
            status, _ = await request(namespace["app"], "/products/validate", {"name": "Pen", "price": -10})
            assert status == (200 if index == 1 else 422)
        count += 1
    # Reproduce the intermediate lesson: Field alone cannot compare two prices.
    intermediate = snapshots[-1].split('    @model_validator(mode="after")')[0]
    intermediate += snapshots[-1][snapshots[-1].index('@app.get("/")'):]
    namespace = {}
    exec(compile(intermediate, "README-before-model-validator", "exec"), namespace)
    status, _ = await request(namespace["app"], "/products/validate", {"name": "Pen", "price": 100, "discount_price": 120})
    assert status == 200
    count += 1
    print(f"PASS: {count} checks (routes, validation boundaries, all 5 README snapshots, and the pre-model-validator demo)")


if __name__ == "__main__":
    asyncio.run(check())
