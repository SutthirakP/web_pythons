# Cookie — จำชื่อผู้ใช้

ตัวอย่างจากคาบเรียน: ให้ server "จำ" ผู้ใช้ได้ทั้งที่ HTTP เป็น stateless โดยใช้ cookie

| Endpoint | หน้าที่ |
|---|---|
| `POST /set-name` | รับชื่อ → สุ่ม `session_id` → เก็บ `session_id → ชื่อ` ไว้ฝั่ง server → ส่ง cookie (HttpOnly, 1 ชม.) |
| `GET /welcome` | อ่าน cookie → ทักทายด้วยชื่อ · ไม่มี cookie ได้ **401** |
| `POST /forget` | ลบ session ฝั่ง server + สั่งเบราว์เซอร์ลบ cookie |

## สิ่งที่ได้เรียนรู้

- **`response.set_cookie(...)`** — สั่งเบราว์เซอร์เก็บ cookie (ส่งไปกับ header `Set-Cookie`)
- **`Cookie()`** — อ่าน cookie ที่เบราว์เซอร์แนบมาเองทุก request
- **`response.delete_cookie(...)`** — logout
- **เก็บแค่ session ID สุ่ม** (`secrets.token_urlsafe`) ไม่เก็บชื่อหรือ user ID ตรง ๆ ใน cookie
- **`httponly=True`** — JavaScript อ่าน cookie ไม่ได้ (กัน XSS)
- bug ที่เคยเจอ: `sessions = dict[str, str] = {}` ต้องเป็น `:` · `http_only` ต้องเป็น `httponly`

เวอร์ชันเต็มในโปรเจกต์หลัก (session ใน Redis + Remember me): [`appm2m/COOKIE.md`](../appm2m/COOKIE.md)

## รัน

```powershell
cd cookie
uv run fastapi dev main.py --port 8010
```

เปิด `http://127.0.0.1:8010/docs` → `POST /set-name` → `GET /welcome`
