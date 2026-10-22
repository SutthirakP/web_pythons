# JWT ตัวแรก

ระบบ login แบบง่ายที่สุด ก่อนนำไปใส่ใน Catalog (`appm2m/auth.py`)

| ไฟล์ | หน้าที่ |
|---|---|
| `hash.py` | ลอง hash รหัสผ่านด้วย `pwdlib` แล้ว verify |
| `auth.py` | `POST /login` ออก token (หมดอายุ 20 นาที), `get_current_user` ตรวจ token, `GET /logout` ใส่ token ลง blacklist |
| `students.py` | `GET /students` เข้าได้เฉพาะคนที่มี token |
| `main.py` | รวม router ทั้งสอง |

## สิ่งที่ได้เรียนรู้

- **ไม่เก็บรหัสผ่านตรง ๆ:** เก็บแค่ hash แล้วใช้ `verify` เทียบ
- **JWT:** token มีข้อมูล `sub` (ชื่อผู้ใช้) กับ `exp` (เวลาหมดอายุ) และเซ็นด้วย `SECRET_KEY` แก้ไม่ได้
- **OAuth2PasswordBearer:** ทำให้ปุ่ม **Authorize** ใน `/docs` ใช้ได้ และดึง token จาก header `Authorization: Bearer ...`
- **Logout ของ JWT:** server ไม่ได้เก็บ session จึงต้องใช้ blacklist (หรือให้ฝั่ง client ลบ token ทิ้ง)

## รัน

ต้องเข้าโฟลเดอร์ก่อน เพราะไฟล์ import กันเองแบบไม่มีจุดนำหน้า

```powershell
cd jwt
uv run fastapi dev main.py --port 8007
```

ใน `/docs` กด **Authorize** ใส่ `admin` / `1234` แล้วลอง `GET /students`
