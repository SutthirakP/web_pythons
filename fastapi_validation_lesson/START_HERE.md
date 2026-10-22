# เริ่มบทเรียน FastAPI ผ่าน VS Code

สร้าง API ตรวจข้อมูลสินค้า โดยผู้เรียนเขียน `main.py` ไฟล์เดียว ส่วน `.venv` ให้ VS Code สร้างให้ ทดลองผ่าน `/docs` ข้อมูลที่ผ่านจะถูกส่งกลับ ยังไม่บันทึกฐานข้อมูล

บทเรียนเดียวกันครอบคลุม BaseModel, Field, field_validator และ model_validator โดยเพิ่มราคาลดที่ต้องต่ำกว่าราคาปกติ ไม่ต้องติดตั้งแพ็กเกจเพิ่ม ขั้นติดตั้งและคำสั่งรันยังเหมือนเดิม

## 0. เตรียมเครื่อง

1. ติดตั้ง [Python](https://www.python.org/downloads/) และ [VS Code](https://code.visualstudio.com/) ถ้ายังไม่มี เครื่องที่ตรวจบทเรียนใช้ Python 3.13.7
2. ใน VS Code เปิด Extensions ติดตั้ง **Python** ของ **Microsoft**
3. หากไม่มีหน้าจัดการ environment ให้ติดตั้ง **Python Environments** ของ Microsoft เพิ่ม

Python เป็นตัวรันภาษา ส่วน extension ช่วย VS Code เลือก Python จัดการ environment และช่วยเขียนโค้ด ต้องมีทั้งสองอย่าง

## 1. เปิดโฟลเดอร์เปล่า

1. เลือก **File → Open Folder**
2. สร้างโฟลเดอร์ใหม่ชื่อ `product_validation_demo` ในหน้าต่างเลือกโฟลเดอร์ แล้วเปิดโฟลเดอร์นั้น
3. ที่ Explorer กด **New File** สร้าง `main.py` และปล่อยว่างไว้ก่อน

เปิดโฟลเดอร์ที่มี `main.py` เป็นโฟลเดอร์หลักของ VS Code อย่าเปิด `.venv` เป็นโฟลเดอร์งาน

## 2. สร้าง environment ผ่านเมนู

1. กด **Ctrl+Shift+P** เปิด Command Palette
2. ค้นหา **Python: Create Environment**
3. เลือก **Venv** แล้วเลือก Python เช่น Python 3.13
4. รอจนเห็น `.venv` ใน Explorer หากถามไฟล์ dependency ให้ข้ามก่อน เพราะจะสอนติดตั้งเอง
5. กด **Ctrl+Shift+P → Python: Select Interpreter** เลือก `.venv` ของงานนี้
6. เปิด **Terminal → New Terminal** หลังเลือก environment ถ้ามี terminal เก่าให้ปิดด้วยไอคอนถังขยะก่อน

| สิ่งที่เลือก | หน้าที่และเหตุผล |
|---|---|
| Command Palette | ค้นหาและเรียกคำสั่งของ VS Code |
| Create Environment | สร้าง environment แยกสำหรับงานนี้ |
| Venv | แยกแพ็กเกจของบทเรียนจากงานอื่น |
| Python 3.13 | เลือก Python ต้นทางที่จะใช้ |
| .venv | โฟลเดอร์ที่เครื่องมือสร้างให้ ไม่ต้องเขียนไฟล์ข้างใน |
| Select Interpreter | กำหนดว่า VS Code จะใช้ Python ตัวไหน |
| New Terminal | เปิด terminal ใหม่หลังเลือก environment |

โดยปกติจะเห็น `(.venv)` หน้าบรรทัด แต่บางการตั้งค่าอาจไม่แสดง ตรวจใน Terminal ของ VS Code ด้วย:

```text
python -c "import sys; print(sys.prefix != sys.base_prefix)"
```

- `python` เรียก Python ที่ terminal ใช้อยู่
- `-c` ให้รันโค้ดในเครื่องหมายคำพูด
- `import sys` โหลดข้อมูลของ Python ที่กำลังทำงาน
- `sys.prefix` คือ environment ปัจจุบัน และ `sys.base_prefix` คือ Python ต้นทาง
- `!=` ตรวจว่าต่างกันหรือไม่ ส่วน `print` แสดงผล
- ต้องได้ **True** ถ้าได้ False ให้เลือก interpreter และเปิด terminal ใหม่ก่อนติดตั้ง

คำสั่งนี้ตรวจว่าเป็น virtual environment แต่ไม่ยืนยันชื่อโครงการ จึงต้องเลือก `.venv` ของงานนี้ด้วย ดู [เอกสาร VS Code](https://code.visualstudio.com/docs/python/environments)

## 3. ติดตั้งแพ็กเกจ

ใน Terminal ของ VS Code ที่ใช้ `.venv` แล้ว พิมพ์:

```text
python -m pip install "fastapi[standard]"
```

| ส่วนของคำสั่ง | ทำอะไร / ทำไมใช้ |
|---|---|
| python | เรียก Python ของ environment ที่เปิดใช้ |
| -m pip | ใช้ตัวติดตั้งแพ็กเกจของ Python ตัวเดียวกัน |
| install | สั่งติดตั้ง |
| "fastapi[standard]" | ชุด FastAPI พร้อมเครื่องมือมาตรฐาน รวม CLI และเซิร์ฟเวอร์ |

ชุดนี้ติดตั้ง Pydantic และ Uvicorn มาด้วย จึงไม่ต้องสั่งแยก:

- **FastAPI** สร้าง API และจัดการคำขอ
- **Pydantic** ตรวจข้อมูลตามโมเดล
- **FastAPI CLI** เพิ่มคำสั่ง `fastapi dev`
- **Uvicorn** เป็นเซิร์ฟเวอร์เบื้องหลังที่ CLI เรียกให้

รอให้ติดตั้งจบโดยไม่มี ERROR ต้องมีอินเทอร์เน็ตระหว่างดาวน์โหลด แล้วตรวจ:

```text
fastapi --version
```

ควรเห็นรุ่นของ CLI ซึ่งไม่จำเป็นต้องมีเลขเดียวกับแพ็กเกจ FastAPI ดู [FastAPI CLI](https://fastapi.tiangolo.com/fastapi-cli/)

ตอนนี้ยังไม่ต้องสร้าง `requirements.txt` หรือไฟล์ทดสอบ ให้เขียน `main.py` ตามบทที่ 4 ใน [คู่มือหลัก](README.md)
