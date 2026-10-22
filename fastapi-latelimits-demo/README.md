# Rate limit + Redis

จำกัดจำนวนครั้งที่เรียก API ได้ต่อนาที กันการยิงรัว / เดารหัสผ่าน และใช้ Redis เป็นที่เก็บตัวนับกับ cache

| ไฟล์ | วิธี | เรียนอะไร |
|---|---|---|
| `main.py` | ใช้ไลบรารี **slowapi** | `@limiter.limit("5/minute")`, handler ตอบ 429 เอง, เก็บตัวนับใน Redis ด้วย `storage_uri` |
| `my_limiter.py` | **เขียนเอง** ด้วย `redis.asyncio` | `INCR` + `EXPIRE` ต่อ IP, dependency ที่ตั้ง limit ต่อ endpoint ได้, `Retry-After`; `/slow-data` cache ผลลัพธ์ใน Redis 30 วินาที |

## สิ่งที่ได้เรียนรู้

- **429 Too Many Requests** + header `Retry-After` บอกว่ารออีกกี่วินาที
- **ทำไมเก็บใน Redis:** restart server แล้วตัวนับไม่หาย, หลาย process ใช้ตัวนับเดียวกัน, `EXPIRE` ลบให้เอง
- **Cache:** ครั้งแรกช้า 5 วินาที ครั้งต่อไปดึงจาก Redis ทันที
- bug ที่เคยเจอ:
  - slowapi บังคับให้ฟังก์ชันที่มี `@limiter.limit` รับ `request: Request`
  - `SlowAPIMiddleware` ไม่รับ `limiter=` (อ่านจาก `app.state.limiter`)
  - ลืม `@` หน้า `app.post(...)` → route ไม่ขึ้นใน `/docs`
  - ใช้ `r.ttl()` แทน `r.incr()` → ตัวนับไม่เคยขึ้น
  - `redis.asyncio.sleep` ไม่มีจริง ต้องใช้ `asyncio.sleep`

นำไปใช้จริงใน Catalog: `appm2m/rate_limit.py`

## รัน

```powershell
docker start my-radis                           # หรือสร้างครั้งแรก: docker run -d --name my-radis -p 6379:6379 redis:7
cd fastapi-latelimits-demo
uv run fastapi dev my_limiter.py                # หรือ main.py
docker exec -it my-radis redis-cli KEYS "*"     # ดูตัวนับใน Redis
```
