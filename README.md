# 🐍 web_pythons — สมุดบันทึกการเรียน FastAPI

> รวมงานและการบ้านวิชาเขียนเว็บด้วย Python
> ตั้งแต่ CRUD พื้นฐาน → ฐานข้อมูลและความสัมพันธ์ → Login → GraphQL / WebSocket / Streaming → Lifespan, Testing, Rate limit, CORS, Cookie

<br>

## 📑 สารบัญ

1. [ภาพรวมโปรเจกต์](#-ภาพรวมโปรเจกต์)
2. [เทคโนโลยีที่ใช้](#-เทคโนโลยีที่ใช้)
3. [ระบบทั้งหมด (Backend)](#-ระบบทั้งหมด-backend)
4. [หน้าเว็บ (Frontend)](#-หน้าเว็บ-frontend)
5. [ฐานข้อมูล (SQL / Redis)](#-ฐานข้อมูล-sql--redis)
6. [โปรเจกต์หลัก: Catalog](#-โปรเจกต์หลัก-catalog)
7. [การติดตั้ง](#-การติดตั้ง)
8. [การรัน](#-การรัน)
9. [ไฟล์ที่จำเป็นต้องมี](#-ไฟล์ที่จำเป็นต้องมี)
10. [โครงสร้างโฟลเดอร์](#-โครงสร้างโฟลเดอร์)
11. [แผนต่อไป](#-แผนต่อไป)

<br>

---

## 🧭 ภาพรวมโปรเจกต์

โปรเจกต์นี้มี **3 ส่วน** ทำงานร่วมกัน

| ส่วน | คืออะไร | อยู่ที่ |
|---|---|---|
| **Backend** | API หลายตัวเขียนด้วย **FastAPI** แยกตามหัวข้อที่เรียน แต่ละตัวรันคนละพอร์ต | โฟลเดอร์ระดับบนสุด (`appm2m/`, `graphql_demo/`, …) |
| **Frontend** | หน้าเว็บ **Next.js + React** ที่เรียก API ข้างบน | `frontend/` |
| **ฐานข้อมูล** | **SQLite** (ไฟล์ `.db` แยกต่อแอป) + **Redis** (ผ่าน Docker) | สร้างอัตโนมัติตอนรันครั้งแรก |

<br>

---

## 🛠 เทคโนโลยีที่ใช้

| ด้าน | เครื่องมือ |
|---|---|
| ภาษา | Python 3.12+, TypeScript |
| Backend framework | FastAPI, Uvicorn, Pydantic |
| ฐานข้อมูล | SQLite + SQLAlchemy (ORM), aiosqlite, Redis |
| Login / ความปลอดภัย | JWT (PyJWT), bcrypt / pwdlib, HttpOnly Cookie, CORS |
| API แบบอื่น | GraphQL (Strawberry), WebSocket, Server-Sent Events |
| AI | TensorFlow / Keras (โมเดลจาก Teachable Machine), Pillow |
| Template | Jinja2 |
| Rate limit | slowapi, Redis `INCR` + `EXPIRE` |
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |
| Test | pytest + FastAPI `TestClient` |
| เครื่องมือ | uv (จัดการ Python package), Docker (Redis), npm |

<br>

---

## ⚙️ ระบบทั้งหมด (Backend)

เรียงตามลำดับที่เรียน — แต่ละโฟลเดอร์มี `README.md` อธิบายละเอียด

| # | โฟลเดอร์ | ระบบ | สิ่งที่ได้เรียน | พอร์ต |
|:-:|---|---|---|:-:|
| 1 | [`crud_basics/`](crud_basics/) | นักศึกษา / สินค้า | GET · POST · PUT · DELETE, Pydantic, เก็บใน list → SQLite | 8000 · 8001 · 8004 |
| 2 | [`appv/`](appv/) | นักศึกษา ↔ เบอร์โทร | **One-to-many** (`ForeignKey` + `relationship`) | 8003 |
| 3 | [`appm2m/`](appm2m/) | **Catalog (โปรเจกต์หลัก)** | Many-to-many + ทุกการบ้านหลังจากนั้น — [ดูด้านล่าง](#-โปรเจกต์หลัก-catalog) | 8002 |
| 4 | [`jwt/`](jwt/) | Login ตัวแรก | สร้าง/ตรวจ JWT, hash รหัสผ่าน, logout ด้วย blacklist | 8007 |
| 5 | [`image_process/`](image_process/) | AI ทายรูปภาพ | โหลดโมเดล Keras แล้วเปิดเป็น API `/predict` | 8006 |
| 6 | [`sse_demo/`](sse_demo/) | Streaming | `StreamingResponse` ส่งทีละคำ, Pydantic Settings + `.env` | 8000 |
| 7 | [`graphql_demo/`](graphql_demo/) | ร้านค้า GraphQL | Query / Mutation ด้วย Strawberry + SQLite | 8005 |
| 8 | [`websocket/`](websocket/) | แจ้งเตือนสินค้า | WebSocket, `ConnectionManager`, broadcast | 8000 |
| 9 | [`upload/`](upload/) | อัปโหลดไฟล์ | `UploadFile`, ตั้งชื่อด้วย `uuid4`, `FileResponse` | 8000 |
| 10 | [`fast-lifespan-demo/`](fast-lifespan-demo/) | Lifespan + Test | โหลดโมเดล/เปิด DB ครั้งเดียว, `TestClient` แบบ `with` | 8000 |
| 11 | [`fastapi-latelimits-demo/`](fastapi-latelimits-demo/) | Rate limit + Cache | slowapi, เขียน limiter เองด้วย Redis, cache ผลลัพธ์ | 8000 |
| 12 | [`reservation-demo/`](reservation-demo/) | จองสินค้าชิ้นสุดท้าย | `asyncio.Lock` กัน race condition, จองชั่วคราว 30 วิ | 8000 |
| 13 | [`fastapi-template-engine/`](fastapi-template-engine/) | Dashboard HTML | Jinja2: `extends` / `block` / `include`, ฟอร์ม + static | 8000 |
| 14 | [`fastapi_validation_lesson/`](fastapi_validation_lesson/) | ตรวจข้อมูลสินค้า | `Field`, `field_validator`, `model_validator` | 8000 |
| 15 | [`cookie/`](cookie/) | จำชื่อผู้ใช้ | `set_cookie`, `Cookie()`, `delete_cookie`, session ID | 8000 |

> ตัวที่ใช้พอร์ต **8000** เป็น demo แยก ให้เปิด **ทีละตัว**

<br>

---

## 🖥 หน้าเว็บ (Frontend)

Next.js อยู่ใน [`frontend/`](frontend/) — เปิดที่ **http://localhost:3000**

| หน้า | ใช้ Backend | ทำอะไรได้ |
|---|---|---|
| `/` | `crud_basics/main.py` (8000) | จัดการรายชื่อนักศึกษาและคะแนน |
| `/products` | `crud_basics/product_db.py` (8001) | เพิ่ม / แก้ / ลบสินค้าใน SQLite |
| `/catalog` | `appm2m` (8002) | **หน้าหลัก** — สินค้า + หมวดหมู่ + รูป + login + แชทบอท + ทดสอบ CORS + ✨ streaming |
| `/graphql-shop` | `graphql_demo` (8005) | ร้านค้าที่เรียกผ่าน GraphQL |

> ⚠️ เปิดด้วย **`localhost`** ไม่ใช่ `127.0.0.1` — cookie login ของ `/catalog` ต้องเป็น site เดียวกับ backend

<br>

---

## 🗄 ฐานข้อมูล (SQL / Redis)

ไฟล์ `.db` **ไม่ได้อยู่ใน repo** (อาจมีข้อมูลผู้ใช้) — แต่ละแอปสร้างไฟล์และตารางให้เองตอนรันครั้งแรก

### SQLite

| ไฟล์ฐานข้อมูล | แอป | ตาราง | ความสัมพันธ์ |
|---|---|---|---|
| `crud_basics/database.db` | student_db | `students` | — |
| `crud_basics/product.db` | product_db | `products` | — |
| `appv/database.db` | appv | `students`, `phones` | **1 : N** — นักศึกษา 1 คนมีหลายเบอร์ |
| `appm2m/catalog.db` | Catalog | `products`, `categories`, `product_categories`, `users` | **N : M** — สินค้า ↔ หมวดหมู่ ผ่านตารางกลาง |
| `graphql_demo/graphql.db` | GraphQL | `products`, `freed_ids` | `freed_ids` จำ id ที่ถูกลบไว้ใช้ซ้ำ |
| `fast-lifespan-demo/app.db` | Lifespan | `predictions_logs` | — (เขียน SQL ตรงด้วย aiosqlite) |

### Redis

| ใช้ทำอะไร | Key | หมดอายุ |
|---|---|---|
| นับจำนวน login (rate limit) | `rate:login:<ip>` | 60 วินาที |
| เก็บ session ของ cookie login | `session:<random id>` | 1 ชั่วโมง / 7 วัน (Remember me) |
| ตัวอย่าง cache / rate limit | `rate:…`, `cache:slow-data` | 30–60 วินาที |

<br>

---

## ⭐ โปรเจกต์หลัก: Catalog

ทุกการบ้านตั้งแต่ many-to-many ถูกต่อยอดลงในโปรเจกต์เดียว — [`appm2m/`](appm2m/) + หน้า `/catalog`

| ระบบ | ไฟล์ | ทำอะไร |
|---|---|---|
| สินค้า ↔ หมวดหมู่ | `models.py`, `main.py` | CRUD สินค้า/หมวดหมู่แบบ many-to-many |
| สมัคร / Login | `auth.py` | hash รหัสผ่านด้วย bcrypt, ออก JWT, เพิ่ม/แก้/ลบได้เฉพาะคนที่ login |
| Cookie login | `session.py`, `auth.py` | จำสถานะ login ด้วย HttpOnly cookie, ติ๊ก **Remember me** ได้, `GET /me` |
| อัปโหลดรูปสินค้า | `upload.py` | ตรวจชนิด/ขนาดไฟล์, ตั้งชื่อสุ่ม, กัน `../` |
| แชทบอท | `chatbot.py` | WebSocket ตอบทีละคำ, แจ้งเตือนทุกคนเมื่อสินค้าเปลี่ยน |
| ✨ เขียนคำอธิบายสินค้า | `streaming.py` | Server-Sent Events ส่งข้อความทีละคำ |
| CORS | `cors.py` | อนุญาตทุก method ยกเว้น HEAD + ปุ่มทดสอบบนหน้าเว็บ |
| Rate limit | `rate_limit.py` | login ได้ 5 ครั้ง/นาที นับใน Redis |
| Lifespan | `main.py` | สร้างตาราง + ทดสอบต่อ DB/Redis ตอนเปิด server, `GET /health` |
| Test | `conftest.py`, `test_main.py` | **40 test** ด้วย pytest (ใช้ DB ชั่วคราว ไม่แตะข้อมูลจริง) |

คู่มือแต่ละเรื่อง: [`RATE_LIMIT.md`](appm2m/RATE_LIMIT.md) · [`CORS_STREAMING.md`](appm2m/CORS_STREAMING.md) · [`COOKIE.md`](appm2m/COOKIE.md) · [`TESTING.md`](fast-lifespan-demo/TESTING.md)

<br>

---

## 📦 การติดตั้ง

### 1. สิ่งที่ต้องมีในเครื่อง

| โปรแกรม | เวอร์ชัน | ใช้ทำอะไร | ดาวน์โหลด |
|---|---|---|---|
| **Python** | 3.12 ขึ้นไป | รัน backend | https://www.python.org/downloads/ |
| **uv** | ล่าสุด | ติดตั้ง package ของ Python | https://docs.astral.sh/uv/ |
| **Node.js** | 20 ขึ้นไป | รันหน้าเว็บ | https://nodejs.org/ |
| **Docker Desktop** | ล่าสุด | รัน Redis | https://www.docker.com/products/docker-desktop/ |
| Git | — | ดึงโค้ด | https://git-scm.com/ |

### 2. ดึงโค้ด

```powershell
git clone https://github.com/SutthirakP/web_pythons.git
cd web_pythons
```

### 3. ติดตั้ง Backend (Python)

```powershell
uv sync
```

คำสั่งเดียวสร้าง `.venv` และติดตั้งทุก package ตาม `pyproject.toml` + `uv.lock` (รวม `pytest` สำหรับ test)

### 4. ติดตั้ง Frontend

```powershell
cd frontend
npm install
cd ..
```

### 5. สร้าง Redis (ครั้งแรกครั้งเดียว)

```powershell
docker run -d --name my-radis -p 6379:6379 --restart unless-stopped redis:7
docker exec -it my-radis redis-cli ping      # ต้องได้ PONG
```

> `--restart unless-stopped` = เปิด Docker Desktop เมื่อไหร่ Redis เปิดตามเอง

### 6. ตั้งค่า `.env` (เฉพาะ `sse_demo`)

```powershell
copy sse_demo\.env.example sse_demo\.env
```

แล้วแก้ `SECRET_KEY` ในไฟล์ `.env` — ไฟล์นี้ **ห้าม commit**

<br>

---

## ▶️ การรัน

### เปิด Backend หลักทั้งหมดในคำสั่งเดียว

```powershell
uv run python run_all.py
```

เปิดพอร์ต **8000 – 8005** พร้อมกัน และเช็ค/เปิด Redis ให้อัตโนมัติ (ต้องเปิด Docker Desktop ไว้) · กด `Ctrl+C` ปิดทั้งหมด

### เปิดหน้าเว็บ

```powershell
cd frontend
npm run dev
```

แล้วเข้า **http://localhost:3000/catalog**

### รันทีละตัว / ทดสอบ

```powershell
uv run fastapi dev appm2m/main.py --port 8002     # Catalog ตัวเดียว
uv run pytest appm2m -v                            # test ของ Catalog (ต้องเปิด Redis)
```

- ทุก backend มีหน้าทดสอบ API ที่ `http://127.0.0.1:<พอร์ต>/docs`
- คำสั่งครบทุกตัว + ตารางพอร์ต + วิธีแก้ปัญหา อยู่ใน **[RUN.md](RUN.md)**

<br>

---

## 📋 ไฟล์ที่จำเป็นต้องมี

| ไฟล์ | หน้าที่ | ถ้าไม่มี |
|---|---|---|
| `pyproject.toml` | รายชื่อ package ของ Python | `uv sync` ไม่รู้จะติดตั้งอะไร |
| `uv.lock` | ล็อกเวอร์ชันให้ทุกเครื่องเหมือนกัน | อาจได้เวอร์ชันที่ไม่เข้ากัน |
| `run_all.py` | เปิด backend หลักทั้งหมด + Redis | ต้องเปิดทีละตัวเอง |
| `frontend/package.json` + `package-lock.json` | package ของหน้าเว็บ | `npm install` ไม่ได้ |
| `image_process/model/keras_model.h5` + `labels.txt` | โมเดล AI ที่เทรนแล้ว | `/predict` ใช้ไม่ได้ |
| `sse_demo/.env` | เก็บ `SECRET_KEY` | ใช้ค่า default (ใช้ได้แค่ตอนพัฒนา) |
| Redis container `my-radis` | rate limit + session login | login หน้า `/catalog` ได้ **503** |

**ไม่ได้อยู่ใน repo (ตั้งใจ):** ไฟล์ `*.db` · รูปที่อัปโหลด (`uploads/`) · `.env` · `.venv/` · `node_modules/` — ทั้งหมดถูกสร้างใหม่ตอนติดตั้ง/รัน

<br>

---

## 🗂 โครงสร้างโฟลเดอร์

```
web_pythons/
├── appm2m/                    ⭐ Catalog — โปรเจกต์หลัก (many-to-many + การบ้านทั้งหมด)
├── appv/                      one-to-many
├── crud_basics/               CRUD พื้นฐาน (list → SQLite)
├── jwt/                       login ด้วย JWT ตัวแรก
├── graphql_demo/              GraphQL + SQLite
├── websocket/                 WebSocket แจ้งเตือน
├── sse_demo/                  Streaming response
├── upload/                    อัปโหลดไฟล์
├── image_process/             AI ทายรูป (Keras)
├── fast-lifespan-demo/        Lifespan + pytest
├── fastapi-latelimits-demo/   Rate limit + Redis cache
├── reservation-demo/          จองสินค้าชิ้นสุดท้าย (Lock)
├── fastapi-template-engine/   Jinja2 template
├── fastapi_validation_lesson/ Pydantic validation
├── cookie/                    Cookie session
├── frontend/                  Next.js (หน้าเว็บทั้งหมด)
├── run_all.py                 เปิด backend หลัก + Redis
├── RUN.md                     คำสั่งรันทั้งหมด + พอร์ต
├── pyproject.toml / uv.lock   dependency ของ Python
└── README.md                  ไฟล์นี้
```

<br>

---

## 🚀 แผนต่อไป

- [ ] **ออกแบบหน้าเว็บใหม่ให้สวยขึ้น** — เลือก UI template ก่อน แล้วค่อยปรับทุกหน้า (`/`, `/products`, `/catalog`, `/graphql-shop`) ให้ใช้ดีไซน์เดียวกัน
- [ ] ทำ layout / navbar กลางที่ทุกหน้าใช้ร่วมกัน
- [ ] รองรับมือถือ (responsive) ทุกหน้า

<br>

---

<sub>จัดทำโดย SutthirakP · รายวิชาเขียนเว็บด้วย Python</sub>
