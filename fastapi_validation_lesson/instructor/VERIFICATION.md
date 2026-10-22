# ผลตรวจบทเรียน

## ผลล่าสุดหลังเพิ่ม model_validator

`python instructor/verify_lesson.py` ผ่าน **37 checks** ครอบคลุมโค้ดสะสมใน README ทั้ง 5 ช่วง และขั้นทดลองก่อนเพิ่ม model_validator

- ราคาปกติ 100 ราคาลด 80 ผ่าน และราคาเท่ากัน/สูงกว่าถูกปฏิเสธด้วย 422 ระดับ body
- ราคาลดศูนย์ ติดลบ ผิดชนิด Infinity และ NaN ถูกปฏิเสธที่ฟิลด์ discount_price
- ไม่ส่งราคาลดหรือส่ง null ยังผ่าน ตัวอย่างเดิมยังใช้งานได้
- ตรวจการแปลงข้อความตัวเลขและกรณีราคาปกติผิดชนิดโดยไม่เกิด server error
- ตรวจขั้นกลางที่มีเพียง Field: ราคาลด 120 เทียบราคาปกติ 100 ยังผ่าน ก่อนเพิ่มกฎระดับโมเดล
- โค้ดฉบับสมบูรณ์ใน README ตรงกับ main.py คำสั่งติดตั้งและรันใน VS Code ไม่เปลี่ยน

ส่วนด้านล่างเป็นประวัติการตรวจรุ่นก่อนเพิ่ม model_validator จำนวน 24 checks ไม่ใช่จำนวนล่าสุด

ตรวจบน Windows ด้วย Python 3.13.7 ใน .venv แยกของบทเรียน

- FastAPI 0.141.1
- Pydantic 2.13.5
- Uvicorn 0.53.0
- dependency ทั้งหมดบันทึกใน requirements-tested.txt

## ผลการตรวจ

- สร้าง environment และติดตั้งจาก requirements.txt สำเร็จ
- `python -m pip check`: No broken requirements found
- `python verify_lesson.py`: ผ่าน 24 checks ครอบคลุม GET /, /docs, /openapi.json, ข้อมูลถูกต้อง, การ strip ชื่อ, default รายละเอียด, ราคาติดลบ/ศูนย์/ข้อความที่แปลงไม่ได้/Infinity/NaN, ชื่อว่างและ whitespace, ฟิลด์บังคับที่หาย, ขอบเขต 100/101 และ 500/501 ตัวอักษร, null และการแปลง "25" เป็น float
- ตรวจโค้ดสะสมใน README ทั้ง 4 ช่วง: import และเรียกแอปได้ ก่อนเพิ่ม Field ราคาติดลบได้ 200 หลังเพิ่ม Field ได้ 422
- โค้ดเต็มช่วงสุดท้ายใน README ตรงกับ main.py
- รัน Uvicorn จริงที่ 127.0.0.1:8765 และส่ง POST ผ่าน PowerShell: ข้อมูลถูกต้องได้ 200 พร้อมชื่อที่ strip แล้ว ราคาติดลบได้ 422 จากนั้นหยุดเซิร์ฟเวอร์

เครื่องมือตรวจ verify_lesson.py เรียกแอปผ่าน ASGI โดยตรง ใช้ standard library และแพ็กเกจของบทเรียน ไม่มีแพ็กเกจทดสอบเพิ่ม เป็นเครื่องมือสำหรับผู้สอน ไม่ใช่เนื้อหาที่ต้องพิมพ์ตามระหว่างคาบ

ตรวจการตอบ HTML ของ /docs แล้ว แต่ไม่ได้ตรวจการแสดงผล Swagger UI ด้วยเบราว์เซอร์จริงหรือการเข้าถึง CDN บนเครื่องผู้เรียน

คู่มือปัจจุบันปรับให้ใช้ VS Code และ fastapi dev main.py พร้อม dependency fastapi[standard] ส่วนโค้ด main.py คงเดิม ย้ายเครื่องมือตรวจไว้ใน instructor ผู้เรียนไม่ต้องเขียนหรือรันไฟล์ส่วนนี้

ตรวจซ้ำหลังปรับแล้ว: ผ่าน 24 checks และ pip check ไม่พบ dependency เสีย ทดลองเปิดด้วย FastAPI CLI dev ที่พอร์ต 8766 และส่ง POST จริงได้ 200 พร้อมชื่อที่ตัดช่องว่างแล้ว จากนั้นหยุดเซิร์ฟเวอร์ การเลือก environment ผ่านเมนู VS Code อ้างอิงเอกสารทางการ ยังไม่ได้ทดสอบคลิกเมนูบนเครื่องผู้เรียน

## รันตรวจซ้ำ

จากโฟลเดอร์ไฟล์เฉลย ใน Terminal ของ VS Code ที่เปิดใช้ environment แล้ว:

```text
python instructor/verify_lesson.py
python -m pip check
```

หากสร้าง environment ใหม่ ให้ติดตั้งด้วย:

```text
python -m pip install -r instructor/requirements-tested.txt
```

ไฟล์นี้บันทึกผลจริงของบทเรียน ไม่ใช่การยืนยันว่าโครงการ web_python66 เดิมผ่านการทดสอบด้วย
