# Streaming Playbook — โค้ดประกอบ

โค้ดชุดนี้คู่กับโน้ต **The Streaming Playbook** — คอมเมนต์ในแต่ละไฟล์บอกไว้แล้วว่าตรงกับ STEP ไหน

| ไฟล์ | ตรงกับ STEP | คืออะไร |
|---|---|---|
| `main.py` | STEP 2, 3, 4, 5 | Hello World → ปัญหา (`/normal`) → ทางแก้ (`/stream`) → พิสูจน์ด้วยเวลาจริง |
| `settings.py`, `.env`, `.env.example` | BONUS | เก็บ `SECRET_KEY` ด้วย Pydantic Settings แทน hardcode |
| `preview.html` | STEP 5 (demo หน้าเว็บ) | เปิดไฟล์นี้ตรง ๆ ในเบราว์เซอร์ กดปุ่มเทียบ ปกติ vs streaming |

## รันตอนนำเสนอ

```powershell
# 1) เปิด server
uv run fastapi dev main.py

# 2) เปิดหน้า demo (คนละ terminal หรือดับเบิลคลิกไฟล์ก็ได้)
start preview.html
```

## ทดสอบ STEP 5 (เวลาจริง) แบบไม่ต้องเปิด server

```powershell
uv run python main.py
```

## ทดสอบ BONUS แบบไม่ต้องเปิด server

```powershell
uv run python settings.py
```
