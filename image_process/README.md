# AI ทำนายรูปภาพ (Keras)

เอาโมเดลที่เทรนจาก Google Teachable Machine มาเปิดเป็น API

| ไฟล์ | หน้าที่ |
|---|---|
| `model/keras_model.h5`, `model/labels.txt` | โมเดลและชื่อคลาส (export จาก Teachable Machine) |
| `keras1.py` | โหลดโมเดลครั้งเดียว, ปรับรูปเป็น 224×224, normalize แล้วทำนาย + `POST /predict` |
| `main.py` | เปิด FastAPI แล้ว include router จาก `keras1.py` |
| `images/watch.jpg` | รูปตัวอย่างไว้ทดสอบ |

## สิ่งที่ได้เรียนรู้

- **โหลดโมเดลครั้งเดียวตอน import** ไม่ใช่ทุก request (โหลดช้า)
- **เตรียมรูปให้ตรงกับตอนเทรน:** ขนาด 224×224, ค่าสี −1 ถึง 1
- **รับไฟล์ด้วย `UploadFile`** แล้วเปิดด้วย Pillow; ไม่ใช่รูปตอบ 400
- โมเดล Teachable Machine เป็น Keras 2 ต้องโหลดด้วย `tf_keras`

## รัน

ต้องอยู่ในโฟลเดอร์นี้ เพราะโค้ดโหลด `model/` แบบ path สั้น

```powershell
cd image_process
uv run python keras1.py                      # ลองทำนาย images/watch.jpg
uv run fastapi dev main.py --port 8006       # เปิดเป็น API แล้วลองที่ /docs
```
