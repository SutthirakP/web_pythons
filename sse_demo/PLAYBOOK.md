# The Streaming Playbook

โน้ตสำหรับเตรียมสอนเพื่อน ๆ เรื่อง `StreamingResponse` ใน FastAPI — เริ่มจากศูนย์ตั้งแต่สร้าง `.venv` ไปจนถึง demo ที่ให้ตัวหนังสือไหลออกมาสดเหมือน ChatGPT จริง

> เพื่อนเลือกไปแล้ว: WebSockets, CORS Middleware, GraphQL, Jinja2, BackgroundTasks (มีคนจองก่อน)
> **เรา → StreamingResponse**

---

## เช็คก่อนเริ่ม: ต้องมีอะไรบ้าง

| หัวข้อ | คำตอบ |
|---|---|
| Python เวอร์ชัน | **3.10 ขึ้นไป** (FastAPI รองรับ 3.8+ แต่ type hint สมัยใหม่ `str \| None` ต้องการ 3.10+) โปรเจกต์นี้ใช้ 3.12.10 |
| ต้องลง pip/uv อะไรเพิ่ม | **ไม่ต้องเลย** — `StreamingResponse` มากับ FastAPI core ตั้งแต่แรก แค่ `fastapi[standard]` ตัวเดียวพอ |
| Import ที่ต้องใช้ | `from fastapi import FastAPI` และ `from fastapi.responses import StreamingResponse` |

---

## STEP 1 — `.venv` คืออะไร ทำไมต้องมี

**.venv** (virtual environment) คือ "กล่องเครื่องมือแยกเฉพาะโปรเจกต์" ปกติเวลาลงแพ็กเกจ Python มันจะไปอยู่ที่เครื่องส่วนกลาง — ถ้ามีหลายโปรเจกต์ที่ต้องการ FastAPI คนละเวอร์ชันกัน จะชนกันทันที `.venv` แก้ปัญหานี้ด้วยการสร้างสภาพแวดล้อม Python แยกกันคนละกล่องให้ทุกโปรเจกต์ ไม่แย่งกัน

```bash
# สร้างโฟลเดอร์โปรเจกต์ใหม่ แล้วเข้าไปข้างใน
mkdir streaming-demo
cd streaming-demo

# ให้ uv สร้างโปรเจกต์ + pyproject.toml ให้
uv init

# ลง FastAPI — uv จะสร้าง .venv อัตโนมัติตอนนี้เลย
uv add "fastapi[standard]"
```

| คำสั่ง | ทำอะไร |
|---|---|
| `mkdir streaming-demo` | สร้างโฟลเดอร์ใหม่ — "บ้าน" ของโปรเจกต์เรา |
| `cd streaming-demo` | ย้ายเข้าไปอยู่ในโฟลเดอร์นั้น คำสั่งถัดไปทำงานในนี้ทั้งหมด |
| `uv init` | ประกาศว่า "โฟลเดอร์นี้คือโปรเจกต์ Python" ได้ไฟล์ `pyproject.toml` |
| `uv add "fastapi[standard]"` | ลง FastAPI + เครื่องมือ dev (uvicorn) เข้า `.venv` ของโปรเจกต์นี้เท่านั้น |

---

## STEP 2 — ไฟล์แรก: Hello World ทีละบรรทัด

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI"}
```

| บรรทัด | ทำอะไร |
|---|---|
| `from fastapi import FastAPI` | ดึงคลาส FastAPI จาก library เข้ามาใช้ |
| `app = FastAPI()` | สร้าง "แอป" — ทุก route ผูกกับตัวแปร `app` ตัวนี้ |
| `@app.get("/")` | decorator — "ถ้ามีใคร GET มาที่ `/` ให้เรียกฟังก์ชันข้างล่างนี้" |
| `async def root():` | ฟังก์ชันที่ทำงานจริงตอนมี request เข้ามา |

รัน: `uv run fastapi dev main.py` แล้วเปิด `http://127.0.0.1:8000/docs` ดู Swagger UI ที่ FastAPI สร้างให้อัตโนมัติ

---

## STEP 3 — ก่อนแก้: client ต้องรอจนกว่าจะครบ

ลองนึกถึงตอน ChatGPT ตอบยาว ๆ — ถ้าต้องรอให้มันคิดจบทั้งหมดก่อนค่อยเห็นคำตอบทีเดียว จะรู้สึกอึดอัดมาก นี่คือแบบปกติของ FastAPI:

```python
MESSAGE = "สวัสดีครับ นี่คือตัวอย่างการส่งข้อความแบบ streaming เหมือน ChatGPT เลยครับ"

@app.get("/normal")
async def normal():
    import asyncio
    await asyncio.sleep(0.9)  # จำลองเวลาที่ใช้ "คิดคำตอบ" ทั้งหมด
    return {"message": MESSAGE}  # ← ส่งทีเดียวทั้งก้อน
```

ผลจริงที่ทดสอบวัดได้: client **ไม่เห็นอะไรเลยจนถึง t ≈ 0.9 วินาที** แล้วข้อความทั้งหมดโผล่มาพร้อมกันทีเดียว

---

## STEP 4 — ทางแก้: StreamingResponse

หัวใจคือเปลี่ยนฟังก์ชันให้เป็น **async generator** (ใช้ `yield` แทน `return`) แล้วห่อด้วย `StreamingResponse`

```python
import asyncio
from fastapi.responses import StreamingResponse  # ← import เพิ่ม

async def word_stream():
    for word in MESSAGE.split(" "):
        yield word + " "          # ← ส่งออกไปทันที ไม่รอคำอื่น
        await asyncio.sleep(0.15)  # จำลองเวลาคิดของแต่ละคำ

@app.get("/stream")
async def stream():
    return StreamingResponse(word_stream(), media_type="text/plain")
```

| บรรทัด | ทำอะไร |
|---|---|
| `async def word_stream():` | ฟังก์ชันนี้ไม่ return ค่าเดียว แต่ "ปล่อย" ค่าออกมาเรื่อย ๆ เรียกว่า generator |
| `yield word + " "` | ส่งคำนี้ออกไปให้ client **ทันที** — ไม่ต้องรอ loop รอบถัดไป |
| `StreamingResponse(word_stream(), ...)` | บอก FastAPI ว่า "อย่ารอให้ generator จบก่อนค่อยส่ง ส่งของที่ yield ออกมาทันทีทุกครั้ง" |
| `media_type="text/plain"` | ชนิดข้อมูลที่ส่ง (ถ้าจะทำ SSE จริงจังใช้ `"text/event-stream"` แทน) |

> **หลักการ:** connection เดิมของ HTTP ยังเปิดค้างไว้ระหว่างส่ง แต่ละ `yield` คือข้อมูลก้อนใหม่ที่วิ่งออกไปทันที จนกว่า generator จะจบเองแล้ว connection ถึงปิด

### ข้อดีของ Streaming เทียบกับ Response ปกติ

| | Response ปกติ (JSONResponse) | StreamingResponse |
|---|---|---|
| ส่งข้อมูลตอนไหน | รอให้ "เสร็จสมบูรณ์" ก่อน แล้วส่งทีเดียว | ส่งออกทันทีที่แต่ละส่วนพร้อม |
| ต้องรู้ขนาดข้อมูลก่อนไหม | รู้ (ระบุ `Content-Length` ใน header ได้) | ไม่จำเป็น (ส่งแบบ chunked transfer) |
| หน่วยความจำฝั่ง server | ต้องพักข้อมูลทั้งก้อนไว้ในตัวแปรก่อนส่ง | ปล่อยออกไปเรื่อย ๆ ไม่ต้องเก็บทั้งก้อนพร้อมกัน |
| Client เห็นผลลัพธ์แรกเมื่อไหร่ | ต่อเมื่อ "ทุกอย่าง" เสร็จ | ทันทีที่ "ส่วนแรก" พร้อม |
| เหมาะกับข้อมูลแบบไหน | ก้อนเล็ก จบไว รู้ผลลัพธ์แน่นอน | ก้อนใหญ่ / ไม่รู้ขนาดล่วงหน้า / ใช้เวลานาน |

**ข้อดีที่พูดในห้องได้ (นอกจาก perceived latency):**

1. **Perceived latency ลดลง** — ผู้ใช้เห็นอะไรบางอย่างทันที ไม่ต้องจ้องหน้าจอเปล่า ๆ ระหว่างรอ (พิสูจน์ด้วยตัวเลขจริงใน STEP 5)
2. **ประหยัดหน่วยความจำฝั่ง server** — ไม่ต้องสร้างข้อความทั้งก้อนในหน่วยความจำก่อนส่ง สำคัญมากกับข้อมูลก้อนใหญ่ เช่น export ไฟล์ CSV ยาว ๆ หรือ AI ที่ตอบยาวหลายพัน token
3. **ใช้ได้แม้ไม่รู้ขนาดข้อมูลล่วงหน้า** — เช่น AI generation ที่ไม่รู้ว่าจะตอบกี่ token ก่อนเริ่มตอบด้วยซ้ำ — response ปกติต้องรอให้รู้ผลลัพธ์สุดท้ายก่อนถึงจะส่งได้
4. **ลดความเสี่ยง connection timeout** — งานที่ใช้เวลานาน ถ้ามีข้อมูลไหลออกไปเรื่อย ๆ ระบบ/proxy จะไม่มองว่า connection "ค้าง" เหมือนตอนรอเงียบ ๆ ทั้งก้อน
5. **ยกเลิกกลางทางได้อย่างมีประโยชน์** — ถ้าผู้ใช้ปิดหน้าเว็บหรือกดหยุดระหว่างทาง server หยุด generator ได้ทันที ไม่ต้องทำงานจนเสร็จทั้งหมดโดยเปล่าประโยชน์

> **ข้อควรระวัง (พูดไว้กันโดนจับผิด):** Streaming ไม่ได้ทำให้ "งานเสร็จเร็วขึ้น" — เวลารวมจริง ๆ ใกล้เคียงเดิมหรืออาจช้ากว่าเล็กน้อยด้วยซ้ำ (มี overhead จากการส่งเป็นชิ้นเล็ก ๆ) สิ่งที่ดีขึ้นคือ **"ผู้ใช้รู้สึกว่าต้องรอน้อยลง"** ไม่ใช่ throughput ที่สูงขึ้น

---

## STEP 5 — พิสูจน์ด้วยเวลาจริง (จุดไฮไลต์ของการ demo)

นี่คือตัวเลขที่วัดได้จริงจากการรันโค้ดชุดนี้ (ไม่ใช่ตัวเลขสมมติ):

| | ปกติ (JSONResponse) | Streaming (StreamingResponse) |
|---|---|---|
| เห็นอะไรครั้งแรก | ไม่เห็นอะไรเลยจนถึง **t = 0.9s** | เห็นคำแรกตั้งแต่ **t = 0.06s** |
| จบทั้งหมด | t ≈ 0.9s | t ≈ 0.84s (ใกล้เคียงกัน) |
| ความรู้สึกของผู้ใช้ | อึดอัด รอเงียบ ๆ | รู้สึกตอบสนองทันที |

```
[t=0.06s] ได้คำ: สวัสดีครับ
[t=0.22s] ได้คำ: นี่คือตัวอย่างการส่งข้อความแบบ
[t=0.37s] ได้คำ: streaming
[t=0.53s] ได้คำ: เหมือน
[t=0.68s] ได้คำ: ChatGPT
[t=0.84s] ได้คำ: เลยครับ
```

> **มุมพูดที่ทำให้ดูเข้าใจลึก:** อย่าพูดแค่ "streaming เร็วกว่า" — พูดว่า **"เวลารวมจริง ๆ ใกล้เคียงเดิม แต่ perceived latency (เวลาที่ผู้ใช้รู้สึกว่าต้องรอ) ลดลงมาก"** เพราะนี่คือสิ่งที่แชทบอท AI อย่าง ChatGPT ใช้จริง ไม่ใช่เพื่อความเร็ว แต่เพื่อ UX

---

## STEP 6 — เตรียมรับมือคำถาม (โดยเฉพาะเทียบกับ WebSockets)

**Q: ต่างจาก WebSockets (ที่เพื่อนเลือก) ตรงไหน?**
StreamingResponse ส่งข้อมูลทางเดียว (server → client) ผ่าน HTTP ปกติแค่ไม่ปิด connection จนกว่าจะส่งครบ — WebSockets เปิด connection พิเศษที่ส่งข้อมูลสองทางได้ตลอดเวลา เหมาะกับแชท/เกมที่ client ต้องส่งกลับด้วย

**Q: ฝั่ง client (JavaScript) ต้องเขียนโค้ดพิเศษไหม?**
ไม่ต้องใช้ library พิเศษ — `fetch()` ธรรมดา แล้วอ่านทีละส่วนด้วย `response.body.getReader()` ก็พอ

**Q: ถ้า generator error กลางทางล่ะ?**
connection จะขาดกลางคัน client จะได้ข้อมูลไม่ครบ ต้องดักจับ exception ในฟังก์ชัน generator เองให้ดี

**Q: ใช้ส่งอย่างอื่นนอกจากข้อความได้ไหม?**
ได้ — ไฟล์ขนาดใหญ่, JSON Lines, หรือทำเป็น Server-Sent Events จริงจัง (`media_type="text/event-stream"` + ฟอร์แมต `data: ...\n\n`) ให้ฝั่ง client ใช้ `EventSource` รับได้เลย

### ตารางเทียบกับ WebSockets

| | StreamingResponse | WebSockets |
|---|---|---|
| ทิศทางข้อมูล | ทางเดียว (server → client) | สองทาง (client ↔ server) |
| อยู่บน protocol ไหน | HTTP ปกติ ไม่ปิด connection จนครบ | Protocol แยก (`ws://`) ต้อง upgrade connection |
| โค้ดฝั่ง client | `fetch()` + อ่าน stream ปกติ | ต้องใช้ `WebSocket` API โดยเฉพาะ |
| เหมาะกับ | AI ตอบคำถาม, log สด, progress bar, ไฟล์ใหญ่ | แชท, เกมเรียลไทม์, ที่ client ต้องส่งกลับตลอด |
| ปิด connection | อัตโนมัติหลัง generator จบ | ต้องจัดการเปิด-ปิดเอง |

---

## STEP 8 — สรุปสั้น ๆ ที่ต้องจำ

| Syntax | ใช้ทำอะไร |
|---|---|
| `StreamingResponse` | class จาก `fastapi.responses` — รับ generator แล้วส่งแต่ละ chunk ทันทีที่ yield |
| `async def` + `yield` | ฟังก์ชันกลายเป็น async generator — ปล่อยข้อมูลทีละส่วน |
| `media_type` | `"text/plain"` สำหรับข้อความทั่วไป, `"text/event-stream"` สำหรับ SSE มาตรฐาน |
| ฝั่ง client อ่านยังไง | `response.body.getReader()` + `TextDecoder` วนอ่านทีละ chunk |
| ต้องลงแพ็กเกจเพิ่มไหม | ไม่ต้อง — มากับ `fastapi[standard]` อยู่แล้ว |

---

## BONUS — เก็บ SECRET_KEY ให้ปลอดภัยด้วย Pydantic Settings

ถ้าเวลาเหลือท้ายเรื่อง แถมนิดนึงได้ — ชี้ให้เห็นว่า `SECRET_KEY = "my-secret-key"` ที่ hardcode ไว้ในโค้ด `auth.py` เป็นปัญหาความปลอดภัยจริง แก้ได้ง่าย ๆ:

```bash
uv add pydantic-settings
```

```env
# .env
SECRET_KEY=ใส่ค่าจริงที่สุ่มเอง-ห้ามใส่ในโค้ด
ALGORITHM=HS256
```

```python
# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str
    algorithm: str = "HS256"

settings = Settings()  # อ่านค่าจาก .env อัตโนมัติ
```

แล้วในโค้ดเดิมแค่เปลี่ยน `SECRET_KEY` → `settings.secret_key` — อย่าลืมใส่ `.env` ใน `.gitignore` ด้วย!

---

## STEP 9 — สคริปต์พูดหน้าห้อง (~6-7 นาที)

| เวลา | ทำอะไร |
|---|---|
| 0:00 | เปิดด้วยของที่ทุกคนรู้จัก — "เคยสังเกตไหมว่า ChatGPT พิมพ์ตอบทีละตัวอักษร ไม่ใช่โผล่มาทีเดียวทั้งก้อน" |
| 1:00 | โชว์แบบปกติก่อน — ยิง `/normal` ให้เห็นค้างเงียบ ๆ ~1 วิ แล้วข้อความโผล่มาทีเดียว |
| 2:30 | เฉลยโค้ดที่แก้ — โชว์ว่าเปลี่ยนแค่ `return` → `yield` กับห่อด้วย `StreamingResponse` |
| 4:00 | **Demo ไลฟ์ — จุดไฮไลต์** — เปิด `preview.html` เทียบสองปุ่ม (ปกติ/streaming) ให้เพื่อนดูตาต่อตา |
| 5:30 | ตัดจบก่อนเพื่อนถาม — เกริ่นเองเลยว่า "นี่ไม่ใช่ WebSockets นะ ต่างกันตรงไหน" แล้วโชว์ตาราง |
| 6:30 | ปิดด้วยของแถม (ถ้าเวลาเหลือ) — ชี้ SECRET_KEY ที่ hardcode ไว้ แล้วโชว์วิธีแก้ด้วย `.env` |

---

*โค้ดประกอบอยู่ในโฟลเดอร์เดียวกัน: `main.py`, `settings.py`, `preview.html` — ดู `README.md` สำหรับวิธีรัน*
