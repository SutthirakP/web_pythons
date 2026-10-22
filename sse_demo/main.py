"""
The Streaming Playbook — โค้ดประกอบการนำเสนอ
ตัวเลข STEP ในคอมเมนต์ตรงกับหัวข้อในโน้ต "The Streaming Playbook" ทุกจุด
รัน: uv run fastapi dev main.py
"""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()

# เปิด CORS + Private Network Access กว้าง ๆ ไว้แค่สำหรับ demo นี้เท่านั้น
# (ให้ preview.html หรือ Artifact เรียกเข้ามาได้) โปรเจกต์จริงห้ามเปิดกว้างขนาดนี้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)


# ============================================================
# STEP 2 — ไฟล์แรก: Hello World
# ============================================================
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI"}


MESSAGE = "สวัสดีครับ นี่คือตัวอย่างการส่งข้อความแบบ streaming เหมือน ChatGPT เลยครับ"


# ============================================================
# STEP 3 — ก่อนแก้: รอให้ข้อความครบทั้งหมดก่อนค่อยส่งทีเดียว (ปัญหา)
# ============================================================
@app.get("/normal")
async def normal():
    await asyncio.sleep(0.15 * len(MESSAGE.split(" ")))  # จำลองเวลา "คิดคำตอบ" ทั้งหมด (~0.9s)
    return {"message": MESSAGE}  # ← ส่งทีเดียวทั้งก้อน ผู้ใช้ไม่เห็นอะไรเลยจนกว่าจะถึงบรรทัดนี้


# ============================================================
# STEP 4 — ทางแก้: StreamingResponse (ส่งออกทันทีทีละคำที่พร้อม)
# ============================================================
async def word_stream():
    for word in MESSAGE.split(" "):
        yield word + " "  # ← ส่งคำนี้ออกไปทันที ไม่รอคำถัดไป
        await asyncio.sleep(0.15)  # จำลองเวลาคิดของแต่ละคำ


@app.get("/stream")
async def stream():
    return StreamingResponse(word_stream(), media_type="text/plain")


# ============================================================
# STEP 5 — พิสูจน์ด้วยเวลาจริง
# รันไฟล์นี้ตรง ๆ (python main.py) เพื่อดูเวลาที่แต่ละคำ "ยิง" ออกมาจริง
# โดยไม่ต้องเปิด server เลย — ทดสอบตัว generator ตรง ๆ
# ============================================================
if __name__ == "__main__":
    import sys
    import time

    sys.stdout.reconfigure(encoding="utf-8")  # กันตัวอักษรไทยเพี้ยนถ้า terminal ใช้ codepage อื่น

    async def _measure():
        start = time.time()
        async for chunk in word_stream():
            print(f"[t={time.time() - start:.2f}s] ได้คำ: {chunk.strip()}")

    asyncio.run(_measure())
