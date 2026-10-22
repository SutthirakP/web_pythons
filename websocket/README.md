# WebSocket — แจ้งเตือนสินค้าแบบ real-time

ทุกหน้าเว็บที่เปิดอยู่ต่อ WebSocket ไว้ พอมีคนเพิ่ม/แก้/ลบสินค้า server จะ **ส่งข้อความหาทุกคนเอง** โดยไม่ต้องกด refresh

| ส่วน | หน้าที่ |
|---|---|
| `GET/POST/PUT/DELETE /products` | CRUD สินค้า (เก็บใน list) |
| `ConnectionManager` | เก็บรายการ connection ที่เปิดอยู่ + `broadcast()` ส่งหาทุกคน |
| `/ws/products` | endpoint WebSocket ที่หน้าเว็บมาต่อ |
| `GET /` | หน้า HTML เล็ก ๆ ที่โหลดสินค้าใหม่ทุกครั้งที่ได้ข้อความ |

## สิ่งที่ได้เรียนรู้

- **HTTP vs WebSocket:** HTTP ต้องให้ client ถามก่อน server ถึงตอบ; WebSocket เปิดค้างไว้ server ส่งมาเมื่อไหร่ก็ได้
- **accept → วนรับ → disconnect:** ต้อง `accept()` ก่อน และจับ `WebSocketDisconnect` เพื่อลบคนที่ปิดหน้าไปแล้ว
- **broadcast:** วนส่งหาทุก connection ใน manager

เวอร์ชันที่สมบูรณ์กว่า (chatbot, ตอบทีละคำ, นับคนออนไลน์) อยู่ใน `appm2m/chatbot.py`

## รัน

```powershell
cd websocket
uv run fastapi dev main.py
```

เปิด `http://127.0.0.1:8000/` สองแท็บ แล้วเพิ่มสินค้าผ่าน `/docs`
