# Catalog — โปรเจกต์หลัก

ร้านค้าที่สินค้า 1 ชิ้นอยู่ได้หลายหมวด และหมวด 1 หมวดมีสินค้าได้หลายชิ้น (many-to-many) แล้วต่อยอดการบ้านทุกสัปดาห์ลงในโปรเจกต์นี้

หน้าเว็บ: `http://localhost:3000/catalog` (โค้ดอยู่ที่ `frontend/src/app/catalog/`)

## สิ่งที่เพิ่มในแต่ละการบ้าน

| หัวข้อ | ไฟล์ | สิ่งที่ได้เรียนรู้ |
|---|---|---|
| Many-to-many | `models.py` | ตารางกลาง `product_categories` + `relationship(secondary=...)` |
| Login / JWT | `auth.py` | สมัครสมาชิก, hash รหัสผ่านด้วย bcrypt, ออก JWT, ล็อกให้เพิ่ม/แก้/ลบได้เฉพาะคนที่ login |
| WebSocket chatbot | `chatbot.py` | `/ws/chat` ตอบทีละคำ (stream), ส่งแจ้งเตือนหาทุกคนเมื่อสินค้าเปลี่ยน, นับคนออนไลน์ |
| อัปโหลดรูปสินค้า | `upload.py` | `POST /upload` → ได้ชื่อไฟล์ → ผูกกับสินค้า, จำกัดชนิด/ขนาดไฟล์, กัน path traversal |
| Lifespan | `main.py` | สร้างตาราง + ทดสอบต่อ DB ตอนเปิด server, ปิด connection ตอนปิด, `/health` |
| Test | `conftest.py`, `test_main.py` | pytest + `TestClient`, ใช้ DB ชั่วคราวไม่แตะข้อมูลจริง, 38 test |
| Rate limit | `rate_limit.py` | login ได้ 5 ครั้ง/นาที นับใน Redis ด้วย `INCR` + `EXPIRE` |
| CORS ห้าม HEAD | `cors.py` | `@app.head("/foo")`, อนุญาตทุก method ยกเว้น HEAD, ทำไม simple request ต้องเช็คเพิ่ม |
| Streaming (SSE) | `streaming.py` | ✨ เขียนคำอธิบายสินค้าส่งทีละคำด้วย `EventSourceResponse` → หน้าเว็บอ่านด้วย `EventSource` |
| Cookie login | `session.py`, `auth.py` | จำสถานะ login ด้วย `HttpOnly` cookie + session ใน Redis, ช่องติ๊ก Remember me (session cookie vs 7 วัน), `GET /me`, logout ลบทั้งสองฝั่ง |

คู่มือละเอียด: [RATE_LIMIT.md](RATE_LIMIT.md) · [CORS_STREAMING.md](CORS_STREAMING.md) · [COOKIE.md](COOKIE.md) · [TESTING.md (lifespan + test)](../fast-lifespan-demo/TESTING.md)

> เปิดหน้าเว็บที่ **`http://localhost:3000/catalog`** (ไม่ใช่ 127.0.0.1) ไม่งั้น cookie login จะไม่ถูกส่ง — ดู [COOKIE.md](COOKIE.md)

## รัน

```powershell
docker start my-radis                              # Redis ต้องเปิดก่อน (ใช้นับ login)
uv run fastapi dev appm2m/main.py --port 8002
uv run pytest appm2m -v                            # รัน test
```

- `http://127.0.0.1:8002/docs` — ลองทุก endpoint
- `http://127.0.0.1:8002/health` — ดูว่า DB กับ Redis พร้อมไหม
