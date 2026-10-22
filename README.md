# web_pythons — สมุดบันทึกการเรียน FastAPI

รวมงานและการบ้านวิชาเขียนเว็บด้วย Python ตั้งแต่ CRUD พื้นฐาน → ฐานข้อมูลและความสัมพันธ์ → Login/JWT → GraphQL, WebSocket, Streaming → Lifespan, Testing, Rate limit ด้วย Redis

แต่ละโฟลเดอร์คือหนึ่งหัวข้อ และมี `README.md` อธิบายว่าเรียนอะไร รันยังไง

## สารบัญ (เรียงตามลำดับที่เรียน)

| # | โฟลเดอร์ | หัวข้อ | สิ่งที่ได้เรียน |
|---|---|---|---|
| 1 | [crud_basics/](crud_basics/) | CRUD พื้นฐาน | GET/POST/PUT/DELETE, Pydantic model, เก็บใน list แล้วต่อ SQLite |
| 2 | [appv/](appv/) | One-to-many | นักศึกษา 1 คนมีเบอร์โทรหลายเบอร์ (`relationship`, `ForeignKey`) |
| 3 | [appm2m/](appm2m/) | **โปรเจกต์หลัก: Catalog** | Many-to-many, JWT, อัปโหลดรูป, WebSocket chatbot, Lifespan, pytest, Rate limit (Redis) |
| 4 | [jwt/](jwt/) | JWT ตัวแรก | สร้าง/ตรวจ token, hash รหัสผ่าน, logout ด้วย blacklist |
| 5 | [image_process/](image_process/) | AI ทำนายรูป | โหลดโมเดล Keras (Teachable Machine) แล้วเปิดเป็น API `/predict` |
| 6 | [sse_demo/](sse_demo/) | Streaming | ส่งคำตอบทีละคำด้วย `StreamingResponse`, Pydantic Settings + `.env` |
| 7 | [graphql_demo/](graphql_demo/) | GraphQL | Query/Mutation ด้วย Strawberry + SQLite, หน้าเว็บยิง GraphQL |
| 8 | [websocket/](websocket/) | WebSocket | แจ้งเตือน real-time ทุกคนเมื่อสินค้าเปลี่ยน |
| 9 | [upload/](upload/) | อัปโหลดไฟล์ | `UploadFile`, ตั้งชื่อไฟล์ด้วย `uuid4`, ส่งไฟล์กลับด้วย `FileResponse` |
| 10 | [fast-lifespan-demo/](fast-lifespan-demo/) | Lifespan + Test | โค้ดตอนเปิด/ปิด server, `TestClient` แบบมี/ไม่มี `with` |
| 11 | [fastapi-latelimits-demo/](fastapi-latelimits-demo/) | Rate limit + Redis | slowapi, เขียน limiter เองด้วย `INCR`/`EXPIRE`, cache ด้วย Redis |
| 12 | [reservation-demo/](reservation-demo/) | จองของชิ้นสุดท้าย | `asyncio.Lock` กันคนแย่งกัน, จองชั่วคราว 30 วินาที |
| 13 | [fastapi-template-engine/](fastapi-template-engine/) | Jinja2 Template | render HTML ฝั่ง server, `extends`/`include`, ฟอร์ม + static files |
| 14 | [fastapi_validation_lesson/](fastapi_validation_lesson/) | Validation | `Field`, `field_validator`, `model_validator` |
| — | [frontend/](frontend/) | หน้าเว็บ (Next.js) | หน้า `/`, `/products`, `/catalog`, `/graphql-shop` ที่เรียก API ข้างบน |

## เริ่มรัน

ต้องมี [uv](https://docs.astral.sh/uv/), Node.js และ Docker (สำหรับ Redis)

```powershell
uv sync                         # ติดตั้ง dependency ของ Python ครั้งแรก
uv run python run_all.py        # เปิด backend หลักทั้งหมด (8000-8005) + เปิด Redis ให้
cd frontend; npm install; npm run dev   # หน้าเว็บ http://localhost:3000
```

คำสั่งทั้งหมดและตารางพอร์ตอยู่ใน [RUN.md](RUN.md)

> ฐานข้อมูล (`*.db`) และไฟล์ที่อัปโหลดไม่ได้อยู่ใน repo — แต่ละแอปสร้างฐานข้อมูลเปล่าให้เองตอนรันครั้งแรก
