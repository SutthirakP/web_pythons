# อัปโหลดไฟล์

ตัวอย่างพื้นฐานของการรับไฟล์และส่งไฟล์กลับ — นำไปต่อยอดเป็นรูปสินค้าใน `appm2m/upload.py`

| Endpoint | หน้าที่ |
|---|---|
| `POST /upload` | รับไฟล์ (`UploadFile`) แล้วบันทึกลง `uploads/` ด้วยชื่อสุ่ม |
| `GET /file/{filename}` | ส่งไฟล์กลับด้วย `FileResponse` ไม่มีตอบ 404 |

## สิ่งที่ได้เรียนรู้

- **`UploadFile`** รับไฟล์แบบ multipart/form-data (ใน `/docs` จะมีปุ่มเลือกไฟล์ให้)
- **ตั้งชื่อใหม่ด้วย `uuid.uuid4()`** กันไฟล์ชื่อซ้ำทับกัน แต่เก็บนามสกุลเดิมไว้
- **bug ที่เคยเจอ:** `uuid.uuid()` ไม่มีจริง (ต้อง `uuid4`), `spilt` → `split`, `os.path.exist` → `exists`
- เวอร์ชันใน `appm2m` เพิ่ม: ต้อง login, จำกัดชนิด/ขนาด, กันชื่อไฟล์แบบ `../` หลุดออกนอกโฟลเดอร์

## รัน

```powershell
cd upload
uv run fastapi dev main.py
```

ไฟล์ที่อัปโหลดไปอยู่ใน `upload/uploads/` (ไม่ได้ขึ้น git)
