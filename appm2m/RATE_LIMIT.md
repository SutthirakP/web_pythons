# Login Rate Limit (Redis) — appm2m (Catalog)

การบ้าน: จำกัดการ login ไม่เกิน **5 ครั้ง/นาที** และเก็บตัวนับไว้ใน **Redis**

ใช้หลักเดียวกับ `fastapi-latelimits-demo/my_limiter.py` (`INCR` + `EXPIRE`)

---

## 1. เปิด Redis ก่อน

```powershell
docker start my-radis                       # เปิด container (ถ้าปิดไปตอนปิดเครื่อง)
docker exec -it my-radis redis-cli ping     # ต้องได้ PONG
```

> container ชื่อ `my-radis` (สะกด **a**) ตามที่สร้างไว้ ถ้า `docker ps` ไม่เห็นแปลว่าปิดอยู่ ให้ `docker start` ก่อน

แล้วเปิด backend ตามปกติ:

```powershell
uv run fastapi dev appm2m/main.py --port 8002
```

ต้องเห็นใน log:

```
[STARTUP] connected to Redis at redis://localhost:6379/0
```

ถ้าเห็น `WARNING: Redis not reachable` = ลืมเปิด Redis → **login จะใช้ไม่ได้ (503)** ส่วนดูสินค้ายังใช้ได้ปกติ

---

## 2. โค้ดอยู่ไหน ทำงานยังไง

| ไฟล์ | ทำอะไร |
|---|---|
| [rate_limit.py](rate_limit.py) | ต่อ Redis + ตัวนับ `limiter()` |
| [main.py](main.py) | lifespan เปิด Redis ตอน start, ปิดตอน shutdown + `/health` บอก `redis_ready` |
| [auth.py](auth.py) | ใส่ `dependencies=[Depends(login_limiter)]` ที่ `POST /login` |

ทุกครั้งที่ยิง `/login`:

```python
key = f"rate:login:{ip}"          # แยกตัวนับตาม IP
count = await r.incr(key)         # +1 แล้วได้ค่าใหม่กลับมา
if count == 1:
    await r.expire(key, 60)       # ครั้งแรก: ตั้งให้ key หายเองใน 60 วิ
if count > 5:
    raise HTTPException(429, ...) # ครั้งที่ 6 ขึ้นไป: บล็อก
```

- **นับทุกครั้ง** ทั้งรหัสถูกและรหัสผิด → กันคนสุ่มเดารหัส (ผิด 5 ครั้งแล้ว ต่อให้ใส่ถูกก็โดนบล็อกจนครบนาที)
- key หายเองเมื่อครบ 60 วินาที = ตัวนับรีเซ็ต
- เก็บใน Redis ไม่ใช่ตัวแปร Python → restart server แล้วตัวนับยังอยู่

### ทำไมไม่ใช้ slowapi แบบ `main.py` ใน demo
ใช้ได้เหมือนกัน แต่แบบเขียนเอง (`my_limiter.py`) เห็นชัดกว่าว่าเขียนอะไรลง Redis และเป็น dependency ธรรมดาของ FastAPI ใส่เฉพาะ endpoint ที่ต้องการได้เลย

---

## 3. ลองเอง

### 3.1 ผ่านหน้าเว็บ
เปิด `http://localhost:3000/catalog` แล้วกด **Log in** ด้วยรหัสผิดรัว ๆ — ครั้งที่ 6 จะขึ้นแถบแดง:

```
Too many login attempts (5 per 60 seconds). Try again in 58 seconds.
```

### 3.2 ผ่าน Swagger
`http://127.0.0.1:8002/docs` → `POST /login` → Try it out → กด Execute 6 ครั้ง
ดู **Response headers**: `x-ratelimit-remaining` ลดลง 4, 3, 2, 1, 0 → ครั้งที่ 6 ได้ **429** พร้อม `retry-after`

### 3.3 ผ่าน PowerShell

```powershell
foreach ($i in 1..6) { curl.exe -s -o NUL -w "attempt $i -> %{http_code}`n" -X POST http://127.0.0.1:8002/login -d "username=x&password=x" }
```

(ต้องพิมพ์ `curl.exe` มี `.exe` เพราะใน PowerShell คำว่า `curl` เฉย ๆ คือคำสั่งอื่น)

ได้ `400` ห้าครั้ง (รหัสผิด) แล้ว `429`

ผลจริงที่ผมรันด้วย curl:

```
attempt 1 -> 400
...
attempt 5 -> 400
attempt 6 -> 429
retry-after: 60
{"detail":"Too many login attempts (5 per 60 seconds). Try again in 60 seconds."}
```

---

## 4. เข้าไปดูใน Redis

ระหว่างที่ตัวนับยังไม่หมดเวลา (ภายใน 1 นาที):

```powershell
docker exec -it my-radis redis-cli KEYS "rate:*"
# rate:login:127.0.0.1

docker exec -it my-radis redis-cli GET rate:login:127.0.0.1
# 6          ← ยิงไปแล้วกี่ครั้งในนาทีนี้

docker exec -it my-radis redis-cli TTL rate:login:127.0.0.1
# 42         ← อีกกี่วินาทีจะรีเซ็ต (-2 = key หายไปแล้ว)

docker exec -it my-radis redis-cli DEL rate:login:127.0.0.1
# ปลดบล็อกทันที ไม่ต้องรอ 1 นาที
```

`/health` ก็บอกสถานะได้: `http://127.0.0.1:8002/health` → `"redis_ready": true`

---

## 5. Test

```powershell
docker start my-radis            # test ต้องใช้ Redis จริง
uv run pytest appm2m -v          # 21 passed
```

Test ใช้ Redis **database 15** (แอปจริงใช้ 0) และล้างให้ทุก test → ไม่ไปยุ่งกับตัวนับจริง

| Test | เช็คอะไร |
|---|---|
| `test_login_allows_5_attempts_then_blocks` | 5 ครั้งแรกได้ 200 (`X-RateLimit-Remaining` ลด 4→0) ครั้งที่ 6 ได้ 429 + `Retry-After` |
| `test_wrong_passwords_count_too` | รหัสผิด 5 ครั้ง → รหัสถูกก็โดน 429 |
| `test_login_counter_is_stored_in_redis` | ยิง 2 ครั้ง → ใน Redis มี `rate:login:testclient = "2"` และมี TTL |
| `test_limit_resets_when_redis_key_expires` | ลบ key (เหมือนรอครบนาที) → login ได้อีก |
| `test_other_endpoints_are_not_limited` | `/products/` ยิง 10 ครั้งไม่โดนบล็อก |
| `test_login_refused_when_redis_is_down` | ไม่มี Redis → 503 |
| `test_health_shows_redis` | `/health` บอก `redis_ready: true` |

ลองทำให้พัง: เปลี่ยน `LOGIN_LIMIT = 5` เป็น `3` ใน `rate_limit.py` แล้วรัน test

```
E           AssertionError: assert '2' == '4'          ← เหลือ 2 ครั้ง แต่ test คาดว่าต้องเหลือ 4
E           AssertionError: assert 429 == 400          ← รหัสผิดครั้งที่ 4 โดนบล็อกเร็วเกินไป
2 failed, 19 passed
```

แก้กลับเป็น `5` → `21 passed`

---

## 6. ปัญหาที่เจอบ่อย

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| login ได้ 503 "Redis is not running" | `docker start my-radis` แล้ว restart backend |
| test ขึ้น `Redis is not running - start it with...` | เหมือนกัน เปิด Redis ก่อนรัน test |
| `KEYS` ว่าง | ยังไม่ได้ยิง login ภายใน 1 นาทีที่ผ่านมา (key หมดอายุแล้ว) |
| ล็อกตัวเองออก ทดสอบต่อไม่ได้ | `docker exec -it my-radis redis-cli DEL rate:login:127.0.0.1` |
