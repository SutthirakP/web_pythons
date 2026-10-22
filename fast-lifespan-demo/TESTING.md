# Lifespan + Test — appm2m (Catalog)

การบ้าน: เพิ่ม lifespan (context manager) ให้โปรเจกต์ product พร้อมเช็คการเชื่อมต่อ DB และเขียน test case (เช่น test add product)

---

## 1. Lifespan คืออะไร ใส่ไว้ตรงไหน

อยู่ใน [main.py](main.py) — โค้ดที่รัน **ครั้งเดียวตอนเปิด server** และ **ครั้งเดียวตอนปิด server**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== ก่อน yield = ตอนเปิด server =====
    Base.metadata.create_all(bind=engine)     # สร้างตาราง
    add_missing_columns()                      # เพิ่มคอลัมน์ image ให้ DB เก่า
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))         # ทดสอบว่าต่อ DB ได้จริง
    app.state.db_ready = True                  # จดไว้ว่า "พร้อมแล้ว"
    app.state.started_at = ...

    try:
        yield                                  # ===== server ทำงานรับ request ตรงนี้ =====
    finally:
        # ===== หลัง yield = ตอนปิด server =====
        app.state.db_ready = False
        engine.dispose()                       # ปิด connection ทั้งหมด

app = FastAPI(lifespan=lifespan)               # ต้องส่ง lifespan เข้าไปตรงนี้ ไม่งั้นไม่รัน
```

และใน [database.py](database.py) ตัว `get_db` จะเช็คก่อนว่า lifespan รันแล้วหรือยัง:

```python
def get_db(request: Request):
    if not getattr(request.app.state, "db_ready", False):
        raise HTTPException(status_code=503, detail="Database is not ready")
    ...
```

แปลว่า **ถ้า lifespan ไม่ได้รัน ทุก endpoint ที่ใช้ DB จะตอบ 503** แทนที่จะพังแบบงง ๆ

---

## 2. เข้าไปเช็คยังไงว่า lifespan ทำงาน

### 2.1 ดู log ตอนเปิด server

```powershell
uv run fastapi dev appm2m/main.py --port 8002
```

ต้องเห็น:

```
[STARTUP] preparing catalog database...
[STARTUP] connected to C:\Users\LENOVO\awesome-project\appm2m\catalog.db
```

กด `Ctrl+C` ปิด จะเห็น:

```
[SHUTDOWN] database connections closed
```

### 2.2 เปิด `/health` ในเบราว์เซอร์

เปิด **http://127.0.0.1:8002/health**

```json
{"status": "online", "db_ready": true, "started_at": "2026-10-07T08:37:09", "products": 1}
```

| field | ความหมาย |
|---|---|
| `db_ready: true` | lifespan รันแล้วและต่อ DB ได้ |
| `started_at` | เวลาที่ server เปิด (lifespan เป็นคนตั้ง) |
| `products` | จำนวนสินค้าใน DB ตอนนี้ (นับจาก DB จริง) |

ทดสอบผ่าน Swagger ได้ที่ http://127.0.0.1:8002/docs → `GET /health` → **Try it out** → **Execute**

---

## 3. รัน test

รันจาก **root โปรเจกต์** (`C:\Users\LENOVO\awesome-project`) ไม่ต้องเปิด server ก่อน

```powershell
uv run pytest appm2m            # รันทั้งหมด แบบสั้น (จุด . = ผ่าน, F = พัง)
uv run pytest appm2m -v         # แสดงชื่อทุก test ว่า PASSED / FAILED
uv run pytest appm2m -k add     # รันเฉพาะ test ที่ชื่อมีคำว่า add
uv run pytest appm2m -x         # หยุดทันทีที่เจอ test แรกที่พัง
uv run pytest appm2m -s         # ให้ print() แสดงออกมาด้วย (จะเห็น [STARTUP] / [SHUTDOWN])
```

ผลที่ถูกต้อง:

```
appm2m\test_main.py ..............                                       [100%]
============================= 14 passed in 8.07s ==============================
```

> **Test ไม่แตะข้อมูลจริง** — [conftest.py](conftest.py) สลับไปใช้ DB ชั่วคราวในโฟลเดอร์ temp และรูปที่อัปโหลดก็ไปลง temp เช่นกัน `catalog.db` กับ `uploads/` ของจริงไม่เปลี่ยน

---

## 4. ไฟล์ test ทำงานยังไง

### 4.1 ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | หน้าที่ |
|---|---|
| [conftest.py](conftest.py) | pytest โหลดเองอัตโนมัติ — ตั้ง DB ชั่วคราว + สร้าง fixture `client`, `auth_headers` |
| [test_main.py](test_main.py) | test case ทั้งหมด |

**กฎของ pytest:** ชื่อไฟล์ต้องขึ้นต้นด้วย `test_` และชื่อฟังก์ชันต้องขึ้นต้นด้วย `test_` ไม่งั้น pytest มองไม่เห็น

### 4.2 `assert` คืออะไร

`assert เงื่อนไข` = "ยืนยันว่าต้องเป็นจริง" ถ้าจริง → ผ่านเงียบ ๆ ถ้าไม่จริง → test พังทันที

```python
assert r.status_code == 200          # ต้องได้ 200
assert product["name"] == "USB Hub"  # ชื่อต้องตรง
assert body["db_ready"] is True      # ต้องเป็น True
assert "99" in r.json()["detail"]    # ข้อความต้องมีเลข 99
```

### 4.3 `with TestClient(app)` คือตัวที่ทำให้ lifespan รัน

นี่คือหัวใจของการบ้าน (เหมือนตัวอย่างใน `fast-lifespan-demo/test_main.py`):

```python
# ไม่มี with → lifespan ไม่รัน → DB ไม่พร้อม → 503
def test_without_with_lifespan_does_not_run():
    client = TestClient(app)
    r = client.get("/products/")
    assert r.status_code == 503

# มี with → startup รันก่อนเข้า block, shutdown รันตอนออกจาก block
def test_lifespan_shutdown_closes_database():
    with TestClient(app) as client:
        assert client.get("/health").json()["db_ready"] is True
    assert app.state.db_ready is False   # ออกจาก with แล้ว = shutdown แล้ว
```

### 4.4 Fixture (`client`, `auth_headers`)

แค่เขียนชื่อเป็น parameter pytest จะเตรียมให้เอง:

```python
def test_add_product(client, auth_headers):
    ...
```

- `client` — ล้าง DB ให้ว่าง แล้วเปิด `with TestClient(app)` ให้ (lifespan รันแล้ว) **ทุก test เริ่มจาก DB ว่างเสมอ** test ไม่กวนกัน
- `auth_headers` — สมัคร + login ให้ แล้วคืน `{"Authorization": "Bearer <token>"}` เอาไปใส่ request ที่ต้อง login

### 4.5 ตัวอย่างเต็ม: test add product

```python
def test_add_product(client, auth_headers):
    # 1. ยิง request
    r = client.post(
        "/products/",
        json={"name": "USB Hub", "description": "4-port", "price": 20},
        headers=auth_headers,
    )
    # 2. เช็คผล
    assert r.status_code == 200
    product = r.json()
    assert product["id"] == 1
    assert product["name"] == "USB Hub"
    assert product["price"] == 20.0

    # 3. เช็คว่าบันทึกลง DB จริง (อ่านกลับด้วย request ใหม่)
    r = client.get("/products/")
    assert [p["name"] for p in r.json()] == ["USB Hub"]
```

รูปแบบทุก test เหมือนกันหมด: **เตรียม → ยิง request → assert ผล**

### 4.6 Test ทั้งหมดที่มี (14 ตัว)

| Test | เช็คอะไร |
|---|---|
| `test_without_with_lifespan_does_not_run` | ไม่มี `with` → 503 |
| `test_with_lifespan_connects_database` | มี `with` → `/health` บอก `db_ready: true` |
| `test_lifespan_shutdown_closes_database` | ออกจาก `with` → `db_ready` กลับเป็น `False` |
| `test_add_product` | เพิ่มสินค้าได้ และบันทึกจริง |
| `test_add_product_requires_login` | ไม่ login → 401 และไม่มีอะไรถูกบันทึก |
| `test_add_product_with_category` | เพิ่มพร้อมหมวดหมู่ (many-to-many) |
| `test_add_product_unknown_category` | หมวดที่ไม่มี → 404 |
| `test_add_product_invalid_price` | ราคาเป็นตัวหนังสือ → 422 |
| `test_add_product_with_image` | อัปโหลดรูป แล้วผูกกับสินค้า |
| `test_update_product` | แก้ชื่อ/ราคา |
| `test_delete_product` | ลบแล้วหาไม่เจอ (404) |
| `test_get_missing_product` | ขอ id ที่ไม่มี → 404 |
| `test_register_duplicate_username` | สมัครชื่อซ้ำ → 409 |
| `test_login_wrong_password` | รหัสผิด → 400 |

---

## 5. ลองทำให้พัง แล้วแก้ (ผลด้านล่างคือของจริงที่รันออกมา)

### Demo 1 — test เขียนค่าที่คาดหวังผิด

แก้ใน `test_main.py` ให้คาดหวังราคาผิด:

```python
assert product["price"] == 25.0      # จริง ๆ ส่งไป 20
```

รัน `uv run pytest appm2m -k test_add_product`:

```
>       assert product["price"] == 25.0
E       assert 20.0 == 25.0
FAILED appm2m/test_main.py::test_add_product - assert 20.0 == 25.0
================== 1 failed, 5 passed, 8 deselected ==================
```

**อ่านยังไง:** บรรทัด `>` คือบรรทัดที่พัง, บรรทัด `E` คือค่าจริง (`20.0`) เทียบกับที่คาดไว้ (`25.0`)
**แก้:** เปลี่ยนกลับเป็น `== 20.0` → ผ่าน

### Demo 2 — ลืมใส่ lifespan ให้ FastAPI

แก้ใน `main.py`:

```python
app = FastAPI()                      # ลืม lifespan=lifespan
```

รัน `uv run pytest appm2m`:

```
E       KeyError: 'access_token'
E       assert False is True
E       assert 503 == 401
E        +  where 503 = <Response [503 Service Unavailable]>.status_code
FAILED appm2m/test_main.py::test_with_lifespan_connects_database - assert Fal...
FAILED appm2m/test_main.py::test_add_product_requires_login - assert 503 == 401
...
```

**อ่านยังไง:** เกือบทุก test พัง และได้ **503** ทั้งหมด = DB ไม่พร้อม = lifespan ไม่ได้รัน
(`KeyError: 'access_token'` มาจาก login ที่ได้ 503 เลยไม่มี token กลับมา)
**แก้:** ใส่กลับเป็น `app = FastAPI(lifespan=lifespan)` → ผ่าน

### Demo 3 — ลืม `db.commit()` ตอนเพิ่มสินค้า

แก้ใน `main.py` ฟังก์ชัน `create_product`:

```python
    db.add(db_product)
    db.flush()          # เดิมเป็น db.commit()
```

รัน `uv run pytest appm2m -k "test_add_product or test_delete"`:

```
>       assert [p["name"] for p in r.json()] == ["USB Hub"]
E       AssertionError: assert [] == ['USB Hub']
E         Right contains one more item: 'USB Hub'
FAILED appm2m/test_main.py::test_add_product - AssertionError: assert [] == [...
FAILED appm2m/test_main.py::test_delete_product - assert 404 == 200
```

**อ่านยังไง:** ตอนสร้างได้ 200 ดูเหมือนสำเร็จ แต่พออ่านกลับได้ `[]` = **ไม่ได้บันทึกลง DB จริง**
นี่คือเหตุผลที่ test ต้องอ่านข้อมูลกลับมาเช็คอีกรอบ ไม่ใช่ดูแค่ status code
**แก้:** เปลี่ยนกลับเป็น `db.commit()` → ผ่าน

> ลองทำเองแล้วอย่าลืมแก้กลับ แล้วรัน `uv run pytest appm2m` ให้ได้ `14 passed` อีกรอบ

---

## 6. เขียน test เพิ่มเอง

ก๊อปแบบนี้ไปแก้ใน `test_main.py`:

```python
def test_add_category(client, auth_headers):
    r = client.post("/categories/", json={"name": "Books"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Books"

    r = client.get("/categories/")
    assert [c["name"] for c in r.json()] == ["Books"]
```

ไอเดีย test อื่น ๆ:
- เพิ่มหมวดชื่อซ้ำ → ต้องได้ 409
- ลบหมวดที่ไม่มี → ต้องได้ 404
- อัปโหลดไฟล์ `.txt` → ต้องได้ 400

---

## 7. ปัญหาที่เจอบ่อย

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `ModuleNotFoundError: No module named 'appm2m'` | รันจากในโฟลเดอร์ `appm2m` — ต้องรันจาก root โปรเจกต์ |
| `collected 0 items` | ชื่อไฟล์หรือชื่อฟังก์ชันไม่ขึ้นต้นด้วย `test_` |
| ได้ 503 ทุก request | ลืม `with TestClient(app)` หรือลืม `lifespan=lifespan` |
| test ผ่านคนเดียว แต่รันรวมแล้วพัง | test พึ่งข้อมูลของ test อื่น — ให้ใช้ fixture `client` ซึ่งล้าง DB ให้ทุกครั้ง |
| `fixture 'client' not found` | `conftest.py` หายหรืออยู่ผิดโฟลเดอร์ (ต้องอยู่ใน `appm2m/`) |
