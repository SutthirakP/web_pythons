# Jinja2 Template — render HTML ฝั่ง server

แทนที่จะส่ง JSON ให้ frontend แยก ให้ FastAPI สร้างหน้า HTML ให้เลยด้วย Jinja2

| ไฟล์ | หน้าที่ |
|---|---|
| `main.py` | `GET /` render หน้า dashboard, `POST /items` รับฟอร์มแล้ว redirect, `DELETE /items/{id}` ลบ (เรียกจาก JS) |
| `templates/base.html` | โครงหน้าหลัก มี `{% block %}` ให้หน้าอื่นเติม + ลิงก์ CSS/JS |
| `templates/components/navbar.html` | ชิ้นส่วนที่ `{% include %}` ใช้ซ้ำ |
| `templates/index.html` | `{% extends "base.html" %}` + ตาราง `{% for %}` / `{% if %}` |
| `static/scripts/app.js` | กดปุ่ม Del → `fetch` DELETE → ลบแถวโดยไม่ reload |

## สิ่งที่ได้เรียนรู้

- **Template inheritance:** `extends` + `block` เขียนโครงหน้าครั้งเดียว
- **Filter:** `{{ items | length }}`, `{{ item.name | title }}`; `{% for %}...{% else %}` แสดงตอนไม่มีข้อมูล
- **`url_for`** สร้างลิงก์จากชื่อ route และ `url_for('static', path=...)` สำหรับไฟล์ static (ต้อง `app.mount("/static", ...)`)
- **ฟอร์ม HTML:** รับด้วย `Form(...)` และชื่อ `name=` ของ input ต้องตรงกับชื่อ parameter
- **POST → Redirect (303)** กันฟอร์มส่งซ้ำตอนกด refresh
- **JS template string** ต้องใช้ backtick `` `/items/${id}` `` ไม่ใช่ `'...'`

## รัน

```powershell
cd fastapi-template-engine
uv run fastapi dev main.py
```
