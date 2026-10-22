# One-to-many — นักศึกษากับเบอร์โทร

นักศึกษา 1 คนมีเบอร์โทรได้หลายเบอร์ (หนึ่งต่อหลาย)

| ไฟล์ | หน้าที่ |
|---|---|
| `database.py` | สร้าง engine/session ชี้ไปที่ `appv/database.db` |
| `models.py` | `StudentDB` กับ `PhoneDB` — `PhoneDB.student_id` เป็น `ForeignKey` และทั้งคู่ผูกกันด้วย `relationship` |
| `schemas.py` | Pydantic: ข้อมูลขาเข้า (`StudentCreate` มี list ของเบอร์) และขาออก (`StudentResponse`) |
| `main.py` | CRUD นักศึกษา พร้อมเบอร์ในครั้งเดียว |

## สิ่งที่ได้เรียนรู้

- **ForeignKey:** ตาราง phones เก็บ `student_id` ชี้กลับไปหานักศึกษา
- **relationship:** `student.phones` ได้ list เบอร์มาเลย ไม่ต้อง query เอง
- **แยกไฟล์ database / models / schemas / main** ให้โค้ดเป็นระเบียบ
- **แยก schema ขาเข้า/ขาออก:** ขาเข้าไม่มี `id` ขาออกมี `id` และ `from_attributes` แปลง ORM → JSON

## รัน

```powershell
uv run fastapi dev appv/main.py --port 8003
```

ทดสอบที่ `http://127.0.0.1:8003/docs` ตัวอย่าง body:

```json
{ "name": "Somchai", "score": 88, "phones": [{ "phone_no": "081-111-1111" }, { "phone_no": "02-222-2222" }] }
```
