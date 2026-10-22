# วิธีรันทุกงานในโปรเจกต์ + พอร์ตทั้งหมด

ทุกคำสั่งรันใน PowerShell ถ้าไม่ได้บอกโฟลเดอร์ ให้รันจาก root โปรเจกต์ (`C:\Users\LENOVO\awesome-project`)

---

## ตารางพอร์ต

| พอร์ต | งาน | ไฟล์ | หน้าเว็บที่ใช้ |
|---|---|---|---|
| **8000** | Students (เก็บใน list) | `crud_basics/main.py` | `http://localhost:3000/` |
| **8001** | Products (SQLite) | `crud_basics/product_db.py` | `http://localhost:3000/products` |
| **8002** | Product ↔ Category (many-to-many) + JWT login | `appm2m/main.py` | `http://localhost:3000/catalog` |
| **8003** | Student ↔ Phone (one-to-many) | `appv/main.py` | ไม่มี ทดสอบผ่าน `/docs` |
| **8004** | Students (SQLite) | `crud_basics/student_db.py` | ไม่มี ทดสอบผ่าน `/docs` |
| **8005** | GraphQL + SQLite | `graphql_demo/main.py` | `http://localhost:3000/graphql-shop` |
| **8006** | ทำนายรูปด้วย Keras | `image_process/main.py` | ไม่มี ทดสอบผ่าน `/docs` |
| **8007** | JWT login ตัวแรก | `jwt/main.py` | ไม่มี ทดสอบผ่าน `/docs` |
| **8000** | Streaming demo | `sse_demo/main.py` | เปิดไฟล์ `sse_demo/preview.html` |
| **3000** | Frontend (Next.js) | `frontend/` | — |

> **ระวัง:** `sse_demo` ต้องใช้พอร์ต **8000** (หน้า `preview.html` ล็อกไว้ที่ 8000) ซึ่งชนกับ `crud_basics/main.py` — **ห้ามรันสองตัวนี้พร้อมกัน** ปิดตัวหนึ่งก่อนเปิดอีกตัว

---

## ทางลัด: เปิด backend ทีเดียวหลายตัว

```powershell
uv run python run_all.py
```

เปิด 6 ตัวพร้อมกัน: **8000, 8001, 8002, 8003, 8004, 8005** กด `Ctrl+C` ครั้งเดียวปิดหมด

ก่อนเปิด backend มันจะเช็ค **Redis** ให้ด้วย (Catalog 8002 ใช้นับ login) ถ้าปิดอยู่จะสั่ง `docker start my-radis` ให้เอง — แค่เปิด Docker Desktop ไว้ก็พอ ถ้าเปิด Redis ไม่ได้ ตัวอื่นยังรันปกติ แต่ login หน้า `/catalog` จะได้ 503

ไม่รวม `image_process`, `jwt`, `sse_demo` เพราะต้อง `cd` เข้าโฟลเดอร์ก่อนรัน ต้องเปิดเองตามด้านล่าง

---

## รันทีละตัว

### Backend ที่รันจาก root

```powershell
uv run fastapi dev crud_basics/main.py --port 8000
uv run fastapi dev crud_basics/product_db.py --port 8001
uv run fastapi dev appm2m/main.py --port 8002
uv run fastapi dev appv/main.py --port 8003
uv run fastapi dev crud_basics/student_db.py --port 8004
uv run fastapi dev graphql_demo/main.py --port 8005
```

### Backend ที่ต้อง `cd` เข้าโฟลเดอร์ก่อน

```powershell
# ทำนายรูป — ต้องอยู่ในโฟลเดอร์นี้เพราะโค้ดโหลด model/ กับ images/ แบบ path สั้น
cd image_process
uv run fastapi dev main.py --port 8006

# JWT ตัวแรก — ไฟล์ข้างใน import กันเองแบบไม่มีจุดนำหน้า
cd jwt
uv run fastapi dev main.py --port 8007

# Streaming demo
cd sse_demo
uv run fastapi dev main.py --port 8000
```

### Frontend

```powershell
cd frontend
npm run dev
```

ต้องเปิด backend ของหน้านั้นไว้ด้วย ไม่งั้นหน้าเว็บจะขึ้น "Failed to fetch" (ดูตารางพอร์ตด้านบนว่าหน้าไหนใช้พอร์ตไหน)

---

## สคริปต์ที่รันตรง ๆ ได้ (ไม่ต้องเปิด server)

```powershell
cd image_process
uv run python keras1.py        # ทำนายรูป images/watch.jpg แล้ว print ผล

cd sse_demo
uv run python main.py          # วัดเวลาที่แต่ละคำ stream ออกมา
uv run python settings.py      # ดูค่าที่อ่านจาก .env
```

---

## รัน test อัตโนมัติ (pytest)

```powershell
docker start my-radis          # Redis ต้องเปิดก่อน (login rate limit + test ใช้)
uv run pytest appm2m -v        # test ของ Catalog (lifespan + สินค้า + login limit) — ไม่ต้องเปิด server
```

วิธีใช้และวิธีอ่านผลอยู่ใน [fast-lifespan-demo/TESTING.md](fast-lifespan-demo/TESTING.md) และ [appm2m/RATE_LIMIT.md](appm2m/RATE_LIMIT.md) เช็คว่า lifespan กับ Redis ทำงานได้ที่ `http://127.0.0.1:8002/health`

> **Catalog (8002) ต้องเปิด Redis ก่อน** (`docker start my-radis`) ไม่งั้น login จะได้ 503

---

## ทดสอบ API ผ่านเบราว์เซอร์

- ทุก backend: `http://127.0.0.1:<พอร์ต>/docs` (Swagger ทดสอบได้ทุก endpoint)
- GraphQL: `http://127.0.0.1:8005/graphql` (หน้า GraphiQL ไว้ลองเขียน query)
- WebSocket แชทบอท: `ws://127.0.0.1:8002/ws/chat` (ใช้ผ่านปุ่มแชทขวาล่างในหน้า `/catalog` — กดปุ่ม `</>` ในหน้าต่างแชทเพื่อดู frame ที่รับส่งจริง, เปิด 2 แท็บแล้วเพิ่ม/แก้/ลบสินค้าในแท็บหนึ่ง อีกแท็บจะเด้งแจ้งเตือนทันที)
- เปิดที่ `http://127.0.0.1:<พอร์ต>/` เฉย ๆ จะได้ `{"detail":"Not Found"}` เป็นเรื่องปกติ เพราะส่วนใหญ่ไม่มี route `/`

---

## บัญชี login (หน้า `/catalog`)

กด **"New here? Register"** เพื่อสมัครก่อน หรือใช้ `admin` / `1234` ที่เคยสมัครไว้แล้ว (ถ้ายังไม่ได้ลบ `appm2m/catalog.db`)

---

## ปัญหาที่เจอบ่อย

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `UnicodeEncodeError: 'charmap' codec...` ตอน `fastapi dev` | terminal ใช้ codepage ภาษาไทย แก้ครั้งเดียวจบ: `[System.Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")` แล้วเปิด terminal ใหม่ |
| `[WinError 10048]` หรือ `10013` | พอร์ตนั้นมีตัวอื่นรันอยู่แล้ว ปิดตัวเดิมก่อน หรือเปลี่ยน `--port` |
| หน้าเว็บขึ้น "Failed to fetch" | backend ของหน้านั้นยังไม่ได้เปิด หรือเปิดผิดพอร์ต/ผิดไฟล์ — เช็คที่ `/docs` ของพอร์ตนั้นว่าเป็นไฟล์ที่ถูก |
| หน้า `/catalog` กดเพิ่ม/แก้/ลบไม่ได้ | ยังไม่ได้ login (ต้องมี token ก่อน) |
| ดูพอร์ตไหนถูกใช้อยู่บ้าง | `netstat -ano \| findstr LISTENING \| findstr ":800"` |
