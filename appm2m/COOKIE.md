# การบ้าน Cookie — จำ User ID / สถานะ login (ส่ง 13 Nov)

ตัวอย่างจากคาบอยู่ที่ `cookie/main.py` — ใน Catalog ทำแบบเดียวกัน แต่เก็บ session ใน **Redis** แทน `dict` (restart server แล้วยังจำได้)

## เดิม vs ตอนนี้

| | เดิม (JWT ใน localStorage) | ตอนนี้ (session cookie) |
|---|---|---|
| หลัง login หน้าเว็บเก็บอะไร | token ไว้ใน `localStorage` | **ไม่เก็บอะไรเลย** — เบราว์เซอร์เก็บ cookie เอง |
| ส่งยังไง | ต้องแนบ `Authorization: Bearer ...` เองทุก request | เบราว์เซอร์แนบ cookie ให้อัตโนมัติ (`credentials: "include"`) |
| JavaScript อ่านได้ไหม | ได้ (ถ้ามี XSS ถูกขโมยได้) | **ไม่ได้** — cookie เป็น `HttpOnly` |
| refresh / เปิดแท็บใหม่ | อ่านจาก localStorage | หน้าเว็บถาม `GET /me` → server ดูจาก cookie |
| logout | ลบ token ฝั่งเบราว์เซอร์ (server ไม่รู้เรื่อง) | server ลบ session ใน Redis **และ** สั่งลบ cookie |

## ทำงานยังไง

```
1) POST /login  (username + password ถูก)
     server: สุ่ม session_id → Redis: session:<id> = {"user_id": 6, "username": "somchai", "remember": false}
     ตอบกลับพร้อม  Set-Cookie: session_id=<id>; HttpOnly; SameSite=lax   (+ Max-Age=604800 ถ้าติ๊ก Remember me)

2) ทุก request ต่อจากนั้น  เบราว์เซอร์แนบ  Cookie: session_id=<id>  ให้เอง
     server: เอา id ไปหาใน Redis → รู้ว่าเป็น user #6

3) GET /me      → {"id": 6, "username": "somchai", "logged_in": true}   (ไม่มี cookie → 401)

4) POST /logout → ลบ session:<id> ใน Redis + Set-Cookie: session_id=""; Max-Age=0
```

cookie เก็บแค่ **เลขสุ่ม** ไม่ได้เก็บ user ID หรือชื่อตรง ๆ — ถ้าเก็บ `user_id=6` ไว้ใน cookie ใครก็แก้เป็น `user_id=1` แล้วกลายเป็นคนอื่นได้

## ไฟล์ที่แก้

| ไฟล์ | อะไร |
|---|---|
| [session.py](session.py) (ใหม่) | สร้าง / อ่าน / ลบ session ใน Redis |
| [auth.py](auth.py) | `/login` ตั้ง cookie, `get_current_user` รับได้ทั้ง cookie หรือ Bearer, เพิ่ม `GET /me`, `/logout` ลบ session + cookie |
| `frontend/src/app/catalog/page.tsx` | เลิกใช้ localStorage, ทุก fetch ใส่ `credentials: "include"`, ตอนเปิดหน้าเรียก `/me`, ช่องติ๊ก **Remember me**, แสดง "Logged in as … (user #id · …)" |

ตั้งค่า cookie ใน [auth.py](auth.py):

```python
response.set_cookie(
    key="session_id",
    value=session_id,
    max_age=REMEMBER_SECONDS if remember else None,   # ติ๊ก = 7 วัน / ไม่ติ๊ก = หายตอนปิดเบราว์เซอร์
    httponly=True,      # JavaScript อ่านไม่ได้ (document.cookie ไม่เห็น)
    samesite="lax",     # เว็บอื่นแอบส่งฟอร์มมาพร้อม cookie ไม่ได้
)
```

> JWT ยังคืนให้ใน `/login` เหมือนเดิม — ปุ่ม **Authorize** ใน `/docs` และ test เดิมยังใช้ได้

---

## ช่องติ๊ก "Remember me"

| | ไม่ติ๊ก (ค่าเริ่มต้น) | ติ๊ก Remember me |
|---|---|---|
| ชนิด cookie | **Session cookie** — ไม่มี `Max-Age` | **Persistent cookie** — `Max-Age=604800` (7 วัน) |
| DevTools ช่อง Expires | `Session` | วันที่อีก 7 วัน |
| ปิดเบราว์เซอร์แล้วเปิดใหม่ | หลุด login | ยัง login อยู่ |
| session ใน Redis | หมดอายุใน 1 ชั่วโมง (กันกรณีไม่เคยปิดเบราว์เซอร์) | หมดอายุใน 7 วัน |
| แถบบนหน้าเว็บ | `until the browser closes` | `remembered for 7 days` |

ฝั่ง backend รับค่าเป็น form field เดียวกับ username/password:

```python
remember: Annotated[bool, Form()] = False   # ไม่ส่งมา (เช่นจาก /docs) = ไม่ติ๊ก
```

> **ตอนโชว์ "ปิดแล้วหลุด":** ใช้หน้าต่าง **Incognito** (Ctrl+Shift+N) — Chrome/Edge ปกติที่เปิด "Continue where you left off" จะกู้ session cookie กลับมาให้ เลยดูเหมือนไม่หลุด วิธีที่ชัวร์ที่สุดคือชี้ช่อง **Expires** ใน DevTools

## วิธีโชว์

```powershell
uv run python run_all.py          # (เปิด Docker Desktop ไว้ก่อน)
cd frontend; npm run dev
```

**ต้องเปิดที่ `http://localhost:3000/catalog`** (ไม่ใช่ `127.0.0.1:3000`) — อธิบายด้านล่าง

1. **Log in** → แถบบนเปลี่ยนเป็น
   `🔓 Logged in as somchai (user #6 · until the browser closes)` — หรือ `remembered for 7 days` ถ้าติ๊ก Remember me
2. **ดู cookie:** F12 → แท็บ **Application** → **Cookies** → `http://localhost:3000`... ไม่เจอ ให้ดูที่ **`http://localhost:8002`** (cookie เป็นของ backend)
   จะเห็น `session_id` ช่อง **HttpOnly ✓**, **SameSite Lax** และช่อง **Expires** เป็น `Session` (ไม่ติ๊ก) หรือวันที่อีก 7 วัน (ติ๊ก)
3. **พิสูจน์ HttpOnly:** แท็บ Console พิมพ์ `document.cookie` → **ไม่มี** `session_id`
4. **กด F5 / ปิดแท็บแล้วเปิดใหม่** → ยัง login อยู่ (เดิมต้องพึ่ง localStorage ตอนนี้ไม่มีอะไรใน localStorage เลย — ดูใน Application → Local Storage ว่างเปล่า)
5. **ดูใน Redis:**
   ```powershell
   docker exec -it my-radis redis-cli KEYS "session:*"
   docker exec -it my-radis redis-cli GET "session:<ก๊อป id จาก cookie>"
   # {"user_id": 6, "username": "somchai"}
   docker exec -it my-radis redis-cli TTL "session:<id>"
   # 3542   ← อีกกี่วินาทีจะหมดอายุ
   ```
6. **Log out** → cookie หายจาก Application, key ใน Redis หาย, refresh แล้วกลับมาเป็นฟอร์ม login
7. **ลองใน `/docs`:** login ที่ `POST /login` ใน `/docs` → แล้วกด `GET /me` เลย ได้ข้อมูล user (เบราว์เซอร์แนบ cookie ให้) โดยไม่ต้องกด Authorize

### ทำไมต้องเปิดที่ `localhost` ไม่ใช่ `127.0.0.1`

เบราว์เซอร์จะส่ง cookie ข้ามไปเฉพาะเว็บ **"same-site"** เท่านั้น (เพราะตั้ง `SameSite=lax`)
- `localhost:3000` → `localhost:8002` = site เดียวกัน (port ไม่นับ) → **ส่ง cookie** ✓
- `127.0.0.1:3000` → `localhost:8002` = คนละ site → **ไม่ส่ง** → refresh แล้วหลุด login

หน้าเว็บจึงเรียก backend ผ่าน `http://localhost:8002` และต้องเปิดหน้าเว็บด้วย `localhost` ให้ตรงกัน

---

## Test

```powershell
uv run pytest appm2m -v      # 38 passed (cookie 7 test + Remember me 3 test)
```

| Test | เช็คอะไร |
|---|---|
| `test_login_sets_session_cookie` | login แล้วได้ `Set-Cookie: session_id=...` มี `HttpOnly`, `SameSite=lax` และไม่มีชื่อ user ในค่า cookie |
| `test_me_without_cookie_is_401` | ไม่มี cookie → 401 |
| `test_me_remembers_user_from_cookie` | มี cookie → `/me` ได้ id + username |
| `test_cookie_alone_can_add_product` | เพิ่มสินค้าได้ด้วย cookie อย่างเดียว ไม่ต้องมี Bearer |
| `test_session_is_stored_in_redis` | ใน Redis มี `session:<id>` = `{"user_id", "username", "remember"}` และ TTL ≤ 3600 |
| `test_fake_cookie_is_rejected` | cookie มั่ว → 401 ทั้ง `/me` และเพิ่มสินค้า |
| `test_logout_forgets_the_cookie` | logout → สั่งลบ cookie + Redis ลบ session + ถึงเก็บ cookie เก่าไว้ก็ใช้ไม่ได้แล้ว |
| `test_without_remember_me_is_a_session_cookie` | ไม่ติ๊ก → cookie ไม่มี `Max-Age`/`Expires`, Redis TTL ≤ 1 ชม. |
| `test_with_remember_me_cookie_lasts_7_days` | ติ๊ก → `Max-Age=604800`, Redis TTL > 1 ชม., `/me` บอก `remember: true` |
| `test_remember_defaults_to_false` | ไม่ส่งช่อง remember มาเลย → ถือว่าไม่ติ๊ก |
