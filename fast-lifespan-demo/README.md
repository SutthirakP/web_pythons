# Lifespan + Test

ตัวอย่างจากคาบเรียน: โค้ดที่ต้องรัน **ครั้งเดียวตอนเปิด server** (โหลดโมเดล, เปิด DB) และ **ครั้งเดียวตอนปิด** (ล้างโมเดล, ปิด DB)

| ไฟล์ | หน้าที่ |
|---|---|
| `main.py` | `lifespan` โหลด "โมเดล" (จำลองว่าช้า 3 วินาที) + เปิด SQLite ด้วย `aiosqlite`; `/predict` คำนวณแล้วบันทึก log; `/logs` ดูประวัติ |
| `test_main.py` | test 2 แบบ: ไม่มี `with` → lifespan ไม่รัน (500) / มี `with` → รัน (200) |
| [TESTING.md](TESTING.md) | **คู่มือ** lifespan + เขียน test ที่นำไปใส่ใน Catalog ทั้งวิธีใช้ `assert`, fixture และตัวอย่างทำให้พังแล้วแก้ |

## สิ่งที่ได้เรียนรู้

- **`@asynccontextmanager` + `yield`:** ก่อน `yield` = startup, หลัง `yield` = shutdown
- **`app.state`** เก็บของที่ใช้ร่วมกันทุก request (โมเดล, connection)
- **`TestClient(app)` เฉย ๆ ไม่รัน lifespan — ต้อง `with TestClient(app) as client:`**
- bug ที่เคยเจอ: พิมพ์ `INTERGER` แทน `INTEGER` → SQLite ไม่ยอมใช้ `AUTOINCREMENT`

## รัน

```powershell
cd fast-lifespan-demo
uv run fastapi dev main.py
uv run pytest -v
```
