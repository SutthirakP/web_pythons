# Frontend — Next.js

หน้าเว็บของโปรเจกต์ เรียก API จาก backend (FastAPI) ที่รันแยกคนละพอร์ต

| หน้า | Backend | ไฟล์ |
|---|---|---|
| `/` | `crud_basics/main.py` · 8000 | `src/app/page.tsx` |
| `/products` | `crud_basics/product_db.py` · 8001 | `src/app/products/page.tsx` |
| `/catalog` | `appm2m` · 8002 | `src/app/catalog/` (page, ChatWidget, ImagePicker, CorsLab, DescribeStream) |
| `/graphql-shop` | `graphql_demo` · 8005 | `src/app/graphql-shop/page.tsx` |

ใช้ **Next.js 16 · React 19 · Tailwind CSS 4** · สี/ธีม (โหมดมืดอัตโนมัติ) อยู่ใน `src/app/globals.css`

## ติดตั้งและรัน

```powershell
npm install
npm run dev
```

เปิด **http://localhost:3000** (ใช้ `localhost` ไม่ใช่ `127.0.0.1` เพื่อให้ cookie login ของ `/catalog` ทำงาน)

ต้องเปิด backend ของหน้านั้นไว้ด้วย — ง่ายสุดคือ `uv run python run_all.py` ที่โฟลเดอร์หลัก

## คำสั่งอื่น

```powershell
npm run build    # build สำหรับ production
npm run lint     # ตรวจโค้ด
```
