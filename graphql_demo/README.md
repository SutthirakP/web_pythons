# GraphQL + SQLite

การบ้าน: (1) แก้ bug id ซ้ำตอนสร้างสินค้า (2) GraphQL ต่อฐานข้อมูลครบ CRUD (3) หน้าเว็บเรียก GraphQL เพื่อเพิ่มข้อมูล

| ไฟล์ | หน้าที่ |
|---|---|
| `database.py`, `models.py` | SQLite + ตาราง `products` และ `freed_ids` (จำ id ที่ถูกลบ) |
| `schema.py` | Strawberry: `Query` (`products`, `product`) และ `Mutation` (`createProduct`, `updateProduct`, `deleteProduct`) |
| `main.py` | เปิด `/graphql` (มีหน้า GraphiQL ให้ลอง) + CORS ให้หน้าเว็บ |
| [GRAPHQL.md](GRAPHQL.md) | **รวมคำสั่ง GraphQL ทั้งหมด** พร้อมตัวอย่าง |

หน้าเว็บ: `http://localhost:3000/graphql-shop` (โค้ดอยู่ที่ `frontend/src/app/graphql-shop/`)

## สิ่งที่ได้เรียนรู้

- **REST vs GraphQL:** GraphQL มี URL เดียว (`/graphql`) และ client เลือกเองว่าอยากได้ field ไหน
- **Query = อ่าน, Mutation = เขียน**
- **ชื่อ field:** เขียน Python เป็น `create_product` แต่ GraphQL แปลงเป็น `createProduct`
- **bug id ซ้ำ:** เดิมใช้ `len(list) + 1` พอลบตัวกลางแล้วสร้างใหม่ id จะชนกัน → ให้ฐานข้อมูลออก id ให้ และนำ id ที่เพิ่งลบกลับมาใช้
- **Variables:** ส่งค่าแยกจากคำสั่ง ไม่ต้องต่อ string เอง

## รัน

```powershell
uv run fastapi dev graphql_demo/main.py --port 8005
```

แล้วเปิด `http://127.0.0.1:8005/graphql`
