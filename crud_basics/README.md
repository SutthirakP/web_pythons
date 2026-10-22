# CRUD พื้นฐาน

จุดเริ่มต้นของวิชา: สร้าง API แบบ CRUD (Create / Read / Update / Delete) เก็บข้อมูลใน list ก่อน แล้วเปลี่ยนไปเก็บใน SQLite

| ไฟล์ | พอร์ต | เรียนอะไร |
|---|---|---|
| `list_example.py` | — | ทบทวน list ของ Python: `extend`, `insert`, `pop`, `index`, `count`, `sorted` |
| `main.py` | 8000 | นักศึกษาเก็บใน list — `GET/POST/PUT/DELETE`, Pydantic `BaseModel`, `HTTPException`, CORS ให้หน้าเว็บเรียกได้ |
| `student_db.py` | 8004 | ย้ายนักศึกษาไปเก็บใน SQLite ด้วย SQLAlchemy: `engine`, `SessionLocal`, `Depends(get_db)` |
| `product_db.py` | 8001 | การบ้าน: CRUD สินค้าใน SQLite ครบทุก method |

## สิ่งที่ได้เรียนรู้

- **Path / Body:** `/students/{id}` รับ id จาก URL ส่วนข้อมูลส่งมาเป็น JSON แล้ว Pydantic ตรวจให้
- **ทำไมต้องฐานข้อมูล:** ข้อมูลใน list หายทุกครั้งที่ restart server แต่ SQLite เก็บลงไฟล์
- **Dependency Injection:** `db: Session = Depends(get_db)` เปิด session ให้ทุก request แล้วปิดให้เองตอนจบ
- **Status code:** 404 เมื่อหาไม่เจอ, 201/200 เมื่อสำเร็จ

## รัน

```powershell
uv run fastapi dev crud_basics/main.py --port 8000
uv run fastapi dev crud_basics/product_db.py --port 8001
uv run fastapi dev crud_basics/student_db.py --port 8004
uv run python crud_basics/list_example.py
```

หน้าเว็บที่ใช้: `http://localhost:3000/` (8000) และ `http://localhost:3000/products` (8001)
