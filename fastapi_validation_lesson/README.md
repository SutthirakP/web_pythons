# เริ่มบทเรียน FastAPI ผ่าน VS Code

สร้าง API ตรวจข้อมูลสินค้า โดยผู้เรียนเขียน `main.py` ไฟล์เดียว ส่วน `.venv` ให้ VS Code สร้างให้ ทดลองผ่าน `/docs` ข้อมูลที่ผ่านจะถูกส่งกลับ ยังไม่บันทึกฐานข้อมูล

เนื้อหาทั้งหมดอยู่ในหัวข้อ **Pydantic Validation** เดียวกัน เรียนจาก BaseModel → Field → field_validator → model_validator โดยช่วงสุดท้ายเพิ่มกฎว่า ถ้ามีราคาลด ราคาลดต้องน้อยกว่าราคาปกติ ไม่ต้องติดตั้งแพ็กเกจเพิ่ม

| เวลาเป้าหมาย | ทำอะไร |
|---|---|
| 0–5 นาที | สร้าง environment และติดตั้งแพ็กเกจ |
| 5–9 นาที | เขียน API แรก รัน และเปิด /docs |
| 9–13 นาที | รับข้อมูลด้วย BaseModel และทดลองก่อนเพิ่มกฎ |
| 13–18 นาที | เพิ่ม Field และทดลองราคา/ชื่อผิดเงื่อนไข |
| 18–22 นาที | เพิ่ม field_validator ตรวจชื่อ |
| 22–28 นาที | เพิ่ม model_validator เปรียบเทียบสองราคา |
| 28–30 นาที | ทดลองผลและอธิบาย error ระดับฟิลด์กับระดับโมเดล |

ตารางเป็นเป้าหมายสำหรับเครื่องพร้อมและผู้เรียนมีพื้นฐาน Python หากต้องพิมพ์ตามช้า ๆ หรือยังไม่รู้จัก class อาจใช้ 35–45 นาที ถ้าเครื่องยังไม่มี Python ควรติดตั้งตัวโปรแกรมก่อนคาบ หากมีแค่ 15 นาที ให้สอนถึง Field และเก็บ validator เป็นบทเสริม


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

ตอนนี้ยังไม่ต้องสร้าง `requirements.txt` หรือไฟล์ทดสอบ เริ่มเขียน `main.py` ตามบทที่ 4 ด้านล่างได้เลย

## 4. เขียน API แรกทีละบรรทัด

เปิดไฟล์ `main.py` ที่สร้างไว้ใน Explorer แล้วเริ่มพิมพ์บรรทัดนี้:

```python
from fastapi import FastAPI
```

`from fastapi` ระบุแพ็กเกจต้นทาง `import FastAPI` นำคลาสสำหรับสร้างแอปมาใช้ ตัวพิมพ์ใหญ่–เล็กต้องตรง

เว้นหนึ่งบรรทัด แล้วเพิ่ม:

```python
app = FastAPI(title="Product Validation Demo")
```

`FastAPI(...)` สร้างแอป `app` เป็นตัวแปรเก็บแอปนั้น `title` กำหนดชื่อที่แสดงบนหน้าเอกสาร API เราต้องมีตัวแปรนี้เพื่อให้ Uvicorn เรียกแอปได้

เว้นบรรทัด แล้วเพิ่มบล็อกนี้ตามลำดับ:

```python
@app.get("/")
def home():
    return {"message": "API is ready"}
```

| บรรทัด | คำอธิบาย |
|---|---|
| `@app.get("/")` | decorator ผูกฟังก์ชันด้านล่างกับคำขอ GET ที่ path `/` โดย GET ใช้ขออ่านข้อมูล |
| `def home():` | สร้างฟังก์ชันชื่อ home ไม่มีพารามิเตอร์ เครื่องหมาย `:` เริ่มบล็อกคำสั่ง |
| `return {"message": "API is ready"}` | คืน dictionary ให้ FastAPI ส่งเป็น JSON โดย message เป็นชื่อ key และข้อความด้านขวาเป็น value |

บรรทัด return เยื้อง 4 ช่องเพื่ออยู่ในฟังก์ชัน Python ใช้ indentation กำหนดขอบเขต ไม่ใช้วงเล็บปีกกาครอบบล็อกแบบบางภาษา

พิมพ์ decorator และฟังก์ชันให้ครบก่อนบันทึก/รัน ระหว่างพิมพ์ทีละบรรทัดโค้ดอาจยังไม่สมบูรณ์

### จุดตรวจที่ 1: main.py ทั้งไฟล์

```python
from fastapi import FastAPI

app = FastAPI(title="Product Validation Demo")


@app.get("/")
def home():
    return {"message": "API is ready"}
```

รันจาก terminal ในโฟลเดอร์บทเรียน:

```text
fastapi dev main.py
```

- `fastapi` เรียกเครื่องมือ CLI
- `dev` เปิดโหมดพัฒนาและ reload เมื่อบันทึกไฟล์ให้เอง
- `main.py` ระบุไฟล์แอปที่มีตัวแปร `app`

ไม่ต้องสร้าง environment หรือติดตั้งใหม่ทุกครั้ง และไม่ใช้ปุ่ม Run Python File เพื่อเปิด API เพราะปุ่มนั้นไม่ได้สั่งเปิดเซิร์ฟเวอร์

เปิด `http://127.0.0.1:8000/` ควรเห็น:

```json
{"message": "API is ready"}
```

`127.0.0.1` คือเครื่องของเรา `8000` คือพอร์ตเริ่มต้นของ Uvicorn จากนั้นเปิด `http://127.0.0.1:8000/docs` จะเห็นหน้า Swagger UI สำหรับทดลอง API

## 5. เพิ่มการรับข้อมูลสินค้าก่อนใส่กฎพิเศษ

เพิ่มบรรทัดนี้ใต้ import เดิม:

```python
from pydantic import BaseModel
```

`BaseModel` เป็นคลาสฐานให้เราประกาศรูปร่างข้อมูล และให้ Pydantic ตรวจข้อมูลตามชนิดที่กำหนด

ใต้บรรทัดสร้าง app และก่อน `@app.get` เพิ่มบล็อกนี้:

```python
class Product(BaseModel):
    name: str
    price: float
    description: str = ""
```

1. `class Product(BaseModel):` สร้างโมเดล Product โดยสืบทอดความสามารถตรวจข้อมูลจาก BaseModel
2. `name: str` กำหนดชื่อเป็นข้อความ ไม่มีค่าเริ่มต้นจึงต้องส่งมา `:` ตรงนี้ใช้ระบุชนิดข้อมูล
3. `price: float` กำหนดราคาเป็นตัวเลขทศนิยมและต้องส่งมา แต่ตอนนี้ยังไม่ได้ห้ามค่าติดลบ
4. `description: str = ""` กำหนดรายละเอียดเป็นข้อความ ถ้าไม่ส่งจะใช้ข้อความว่าง การมีค่าเริ่มต้นไม่ได้แปลว่ารับ null ได้

เพิ่ม endpoint นี้ท้ายไฟล์ โดยเริ่ม decorator ชิดซ้าย ไม่อยู่ในคลาส Product:

```python
@app.post("/products/validate")
def validate_product(product: Product):
    return {"message": "Product is valid", "product": product.model_dump()}
```

1. `@app.post(...)` รับคำขอ POST ที่ส่งข้อมูลให้เซิร์ฟเวอร์ตรวจ เลือก POST เพราะส่ง JSON body ที่มีข้อมูลสินค้า
2. `def validate_product(product: Product):` ให้ FastAPI อ่าน request body และตรวจด้วยโมเดล Product ก่อนเรียกฟังก์ชัน หากตรวจไม่ผ่านจะไม่เข้ามาทำ return ในฟังก์ชันนี้
3. `return ...` ส่งข้อความกับข้อมูลกลับ `product.model_dump()` แปลงโมเดลเป็น dictionary ส่วน FastAPI จะจัดการส่งเป็น JSON

ใช้ `def` ธรรมดาได้ เพราะตัวอย่างไม่มีงาน I/O ที่ต้อง await ไม่จำเป็นต้องเพิ่ม `async` เพื่อทำ validation

### จุดตรวจที่ 2: main.py ทั้งไฟล์

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Product Validation Demo")


class Product(BaseModel):
    name: str
    price: float
    description: str = ""


@app.get("/")
def home():
    return {"message": "API is ready"}


@app.post("/products/validate")
def validate_product(product: Product):
    return {"message": "Product is valid", "product": product.model_dump()}
```

บันทึกไฟล์ รอ server reload และ refresh หน้า /docs → กด POST /products/validate → Try it out → แทนที่ Request body ด้วย:

```json
{"name": "Pen", "price": -10}
```

กด Execute แล้วดู **Server response** ควรได้ 200 และ price -10 แสดงว่าชนิด float อย่างเดียวยังไม่ห้ามราคาติดลบ อย่าสับสนกับส่วน Responses ที่เป็นรายการเอกสารด้านล่าง

## 6. เพิ่มกฎด้วย Field

แก้ import บรรทัดที่สองเป็น:

```python
from pydantic import BaseModel, Field
```

เพิ่ม `Field` เพื่อประกาศข้อจำกัดของแต่ละช่องข้อมูล จากนั้นแทนที่สามบรรทัดใน Product ด้วย:

```python
class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, allow_inf_nan=False)
    description: str = Field(default="", max_length=500)
```

อธิบายทีละบรรทัด:

1. `class Product(BaseModel):` ใช้คลาสเดิม ไม่สร้าง Product ซ้ำอีกคลาส
2. `name: str = Field(min_length=1, max_length=100)` รับชื่อยาว 1–100 ตัวอักษร จึงห้าม `""` แต่ยังไม่ได้ห้าม `"   "` เพราะช่องว่างนับเป็นตัวอักษรด้วย `Field` ที่ไม่มี default ยังคงเป็นฟิลด์บังคับ
3. `price: float = Field(gt=0, allow_inf_nan=False)` ใช้ `gt` ย่อจาก greater than ราคา 0 และค่าติดลบไม่ผ่าน ส่วน `allow_inf_nan=False` ห้ามค่าพิเศษ infinity/NaN ที่ไม่ใช่ราคาจำนวนจำกัดตามปกติ
4. `description: str = Field(default="", max_length=500)` ถ้าไม่ส่งรายละเอียดใช้ `""` และถ้าส่งต้องยาวไม่เกิน 500 ตัวอักษร

### จุดตรวจที่ 3: main.py ทั้งไฟล์

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Product Validation Demo")


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, allow_inf_nan=False)
    description: str = Field(default="", max_length=500)


@app.get("/")
def home():
    return {"message": "API is ready"}


@app.post("/products/validate")
def validate_product(product: Product):
    return {"message": "Product is valid", "product": product.model_dump()}
```

บันทึกและ refresh /docs แล้วส่ง `{"name":"Pen","price":-10}` อีกครั้ง คราวนี้ควรได้ 422 ลองเปลี่ยน price เป็น 10 แล้วควรได้ 200

ขั้นนี้อธิบายกฎพื้นฐานตามแนวทาง [FastAPI Body Fields](https://fastapi.tiangolo.com/tutorial/body-fields/)

## 7. เพิ่ม validator สำหรับชื่อที่มีแต่ช่องว่าง

ลองส่ง `{"name":"   ","price":10}` ในขั้นที่ 6 จะยังผ่าน เราต้องเพิ่มกฎให้ตรวจความหมายของข้อความหลังตัดช่องว่างหัว–ท้าย

แก้ import เป็น:

```python
from pydantic import BaseModel, Field, field_validator
```

`field_validator` เป็น decorator ของ Pydantic รุ่น 2 สำหรับผูกฟังก์ชันตรวจข้อมูลกับชื่อฟิลด์

ภายในคลาส Product ใต้ description เว้นหนึ่งบรรทัด แล้วเพิ่มทีละบรรทัดตามนี้:

```python
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_name = value.strip()
        if not cleaned_name:
            raise ValueError("Product name must not be blank")
        return cleaned_name
```

| บรรทัด | ทำอะไร | ทำไมต้องใช้ |
|---|---|---|
| `@field_validator("name")` | ให้ Pydantic เรียกฟังก์ชันนี้กับช่อง name โดยค่าเริ่มต้นทำงานหลังตรวจชนิดและ Field | เพิ่มกฎเฉพาะที่เราต้องการ |
| `@classmethod` | กำหนดเมธอดให้รับคลาสเป็นอาร์กิวเมนต์แรก | ใช้รูปแบบ class method สำหรับ validator นี้ |
| `def validate_name(cls, value: str) -> str:` | ประกาศฟังก์ชัน รับ cls ซึ่งอ้างถึงคลาสและ value ซึ่งเป็นข้อความ พร้อมระบุว่าจะคืนข้อความ | บอกข้อมูลที่รับและผลลัพธ์ที่ส่งกลับ แม้ตัวอย่างนี้ไม่ต้องใช้ cls ภายใน |
| `cleaned_name = value.strip()` | ตัดช่องว่างรวมถึง whitespace หัว–ท้าย แล้วเก็บค่าใหม่ | ทำให้ชื่อที่มีแต่ช่องว่างกลายเป็นข้อความว่าง |
| `if not cleaned_name:` | ตรวจว่าข้อความหลังตัดว่างหรือไม่ | ข้อความว่างมีค่าความจริงเป็น False |
| `raise ValueError(...)` | แจ้งว่าค่านั้นใช้ไม่ได้ | Pydantic รวมเป็น validation error และ FastAPI ตอบ 422 |
| `return cleaned_name` | คืนชื่อที่ผ่านและตัดช่องว่างแล้ว | ค่าที่คืนจะกลายเป็น name ในโมเดล หากลืม return ฟังก์ชันจะคืน None |

ตำแหน่งย่อหน้า: decorator และ def อยู่ 4 ช่องใน class, เนื้อหาเมธอดอยู่ 8 ช่อง, raise อยู่ 12 ช่องเพราะอยู่ใน if ส่วน return กลับมา 8 ช่องเพื่อทำงานเมื่อไม่เข้า if

ข้อสังเกต: validator นี้ทำงานหลัง Field ดังนั้นชื่อดิบยาวเกิน 100 ตัวอักษรจะถูกปฏิเสธก่อน strip แม้ว่าตัดช่องว่างแล้วอาจสั้นลงก็ตาม นี่คือกติกาของบทนี้

ดูหลักการ validator เพิ่มเติมใน [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)

## 8. จุดตรวจที่ 4: โค้ดหลังเพิ่ม field_validator

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Product Validation Demo")


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, allow_inf_nan=False)
    description: str = Field(default="", max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_name = value.strip()
        if not cleaned_name:
            raise ValueError("Product name must not be blank")
        return cleaned_name


@app.get("/")
def home():
    return {"message": "API is ready"}


@app.post("/products/validate")
def validate_product(product: Product):
    return {"message": "Product is valid", "product": product.model_dump()}
```

### 8.1 เพิ่มราคาลดและตรวจหลายฟิลด์ด้วย model_validator

ยังเป็น Pydantic Validation เหมือนเดิม แต่คราวนี้ต้องใช้ข้อมูลสองช่องประกอบกัน เช่น ราคาปกติ 100 และราคาลด 120 ต่างก็เป็นจำนวนมากกว่า 0 จึงผ่าน Field ทั้งคู่ แต่ไม่ถูกกฎของร้านค้า

กำหนดให้ `discount_price` เป็น **ราคาขายหลังลดแล้ว** ไม่ใช่จำนวนเงินที่ลดออก ถ้าไม่ส่งหรือส่ง null หมายถึงไม่มีราคาลด เพื่อให้ตัวอย่างก่อนหน้านี้ยังใช้ได้

**ขั้นที่ 1 — เพิ่มชื่อที่ import** แทนที่ import ของ Pydantic ด้วย:

```python
from pydantic import BaseModel, Field, field_validator, model_validator
```

เพิ่ม `model_validator` เพื่อประกาศฟังก์ชันตรวจข้อมูลทั้งโมเดล ใช้แพ็กเกจเดิม ไม่ต้อง pip install เพิ่ม

**ขั้นที่ 2 — เพิ่มฟิลด์** ใต้ description ภายในคลาส Product ย่อหน้า 4 ช่อง:

```python
    discount_price: float | None = Field(default=None, gt=0, allow_inf_nan=False)
```

| ส่วนของบรรทัด | ทำอะไร / ทำไมใช้ |
|---|---|
| `discount_price` | ชื่อช่องราคาขายหลังลด |
| `float \| None` | รับตัวเลขหรือ None ซึ่งแทนการไม่มีราคาลด; JSON ใช้ null แทน None |
| `default=None` | ถ้าไม่ส่งช่องนี้ ให้ถือว่าไม่มีราคาลด การยอมรับ None กับการมีค่าเริ่มต้นเป็นคนละเรื่อง |
| `gt=0` | ถ้าส่งตัวเลข ราคาลดต้องมากกว่า 0 |
| `allow_inf_nan=False` | ห้ามค่าพิเศษ infinity และ NaN เช่นเดียวกับราคาปกติ |

บันทึกแล้วทดลอง `{"name":"Pen","price":100,"discount_price":120}` ตอนนี้ยังได้ 200 เพราะ Field ตรวจราคาลดแยกจากราคาปกติ นี่คือปัญหาที่ขั้นต่อไปจะแก้

**ขั้นที่ 3 — เพิ่มเมธอดตรวจสองราคา** ภายใน Product ใต้ validate_name โดย decorator และ def ย่อหน้า 4 ช่องเท่ากัน อย่าใส่ไว้ภายในเมธอด validate_name:

```python
    @model_validator(mode="after")
    def validate_discount(self) -> "Product":
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("Discount price must be less than regular price")
        return self
```

อธิบายทีละบรรทัด:

1. **`@model_validator(mode="after")`** ให้ตรวจหลังจากฟิลด์ทั้งหมดผ่านการตรวจแล้ว จึงใช้ค่าที่แปลงชนิดแล้วมาประกอบกันได้ ถ้า price ผิดชนิดหรือ name ไม่ผ่าน จะยังไม่เรียก after validator นี้
2. **`def validate_discount(self) -> "Product":`** สร้างเมธอดที่รับข้อมูลสินค้าทั้งก้อนผ่าน self และคืน Product กลับ การใส่ชื่อ Product ในเครื่องหมายคำพูดทำให้ระบุชนิดของคลาสที่กำลังประกาศได้ ใช้ self เพราะต้องอ่านค่าของสินค้ารายการนี้ จึงไม่ใส่ @classmethod เหมือนตัวอย่าง field_validator
3. **`if self.discount_price is not None and self.discount_price >= self.price:`** ตรวจว่ามีราคาลดก่อน แล้วจึงเทียบว่ามากกว่าหรือเท่าราคาปกติหรือไม่ and จะหยุดเมื่อเงื่อนไขแรกเป็น False จึงไม่เอา None ไปเปรียบเทียบกับตัวเลข ส่วน >= รวมกรณีราคาเท่ากันด้วย
4. **`raise ValueError(...)`** ปฏิเสธข้อมูลเมื่อราคาลดไม่ต่ำกว่าราคาปกติ ทำให้ FastAPI ตอบ 422
5. **`return self`** คืนโมเดลสินค้าที่ผ่านกฎแล้ว ต้องอยู่ระดับย่อหน้าเดียวกับ if และต้องคืนโมเดลทั้งก้อน ไม่ใช่คืนแค่ราคาหรือ dictionary

ตามรูปแบบ [Pydantic Model Validators](https://docs.pydantic.dev/latest/concepts/validators/#model-validators) ส่วน field_validator ตรวจค่าของฟิลด์หนึ่ง และ model_validator ใช้ตรวจโมเดลโดยรวม

### 8.2 จุดตรวจที่ 5: main.py ฉบับสมบูรณ์

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator, model_validator

app = FastAPI(title="Product Validation Demo")


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, allow_inf_nan=False)
    description: str = Field(default="", max_length=500)
    discount_price: float | None = Field(default=None, gt=0, allow_inf_nan=False)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_name = value.strip()
        if not cleaned_name:
            raise ValueError("Product name must not be blank")
        return cleaned_name

    @model_validator(mode="after")
    def validate_discount(self) -> "Product":
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("Discount price must be less than regular price")
        return self


@app.get("/")
def home():
    return {"message": "API is ready"}


@app.post("/products/validate")
def validate_product(product: Product):
    return {"message": "Product is valid", "product": product.model_dump()}
```

กด Ctrl+S รอ reload แล้ว refresh /docs เพื่อให้เห็นฟิลด์ใหม่ ตัวอย่างทั้งหมดหลังจากนี้ใช้โค้ดฉบับสมบูรณ์นี้

โครงสร้างโฟลเดอร์ที่ผู้เรียนสร้าง:

```text
product_validation_demo/
├── .venv/
└── main.py
```

## 9. ทดลองและอ่านผล

ใช้ /docs → POST /products/validate → Try it out → วาง JSON → Execute ทุกครั้งหลังแก้กฎให้บันทึกไฟล์และรอ reload ก่อน

### กรณี A: ข้อมูลถูกต้อง

```json
{"name": "  ปากกา  ", "price": 25}
```

สถานะ 200 และผลลัพธ์:

```json
{
  "message": "Product is valid",
  "product": {
    "name": "ปากกา",
    "price": 25.0,
    "description": "",
    "discount_price": null
  }
}
```

เห็นว่า validator ตัดช่องว่าง, price เป็น float, รายละเอียดใช้ default และ discount_price เป็น null เพราะไม่ได้ส่งมา การตอบ 200 หมายถึงตรวจสำเร็จ ไม่ใช่บันทึกสินค้าแล้ว จึงไม่ได้ใช้ 201 Created

### กรณี B: ราคาผิด

```json
{"name": "Pen", "price": -10}
```

สถานะ 422 ตัวอย่างส่วนสำคัญของ response:

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "price"],
      "msg": "Input should be greater than 0",
      "input": -10,
      "ctx": {"gt": 0}
    }
  ]
}
```

- `detail` เป็นรายการข้อผิดพลาด อาจมีมากกว่าหนึ่งรายการ
- `type` บอกชนิดข้อผิดพลาด
- `loc` บอกว่าผิดตรง price ใน request body
- `msg` อธิบายเงื่อนไขที่ไม่ผ่าน
- `input` แสดงค่าที่ส่งมา
- `ctx` แสดงค่าประกอบกฎ เช่น gt เท่ากับ 0

รายละเอียดปลีกย่อยอาจต่างกันตามรุ่น แต่สถานะและตำแหน่งฟิลด์ควรเป็นไปตามกฎ

### กรณี C: ชื่อมีแต่ช่องว่าง

```json
{"name": "   ", "price": 25}
```

คาดหวัง 422, loc เป็น body/name และข้อความมี `Product name must not be blank`

### กรณี D: ขาดฟิลด์บังคับ

```json
{"name": "Pen"}
```

คาดหวัง 422 ที่ price เพราะไม่ได้ตั้งค่าเริ่มต้นให้ฟิลด์นี้

### กรณี E: ราคาลดสัมพันธ์กับราคาปกติ

ทดลองทีละรายการใน /docs:

| Request body | ผลที่ควรเห็น |
|---|---|
| `{"name":"Pen","price":100,"discount_price":80}` | 200 ราคาลดต่ำกว่าราคาปกติ |
| `{"name":"Pen","price":100,"discount_price":100}` | 422 ราคาเท่ากันไม่ถือว่าลด |
| `{"name":"Pen","price":100,"discount_price":120}` | 422 ราคาลดสูงกว่าราคาปกติ |
| `{"name":"Pen","price":100,"discount_price":0}` | 422 จาก Field เพราะราคาลดต้องมากกว่า 0 |
| `{"name":"Pen","price":100,"discount_price":null}` | 200 ไม่มีราคาลด |
| `{"name":"Pen","price":100}` | 200 ไม่ส่งราคาลดก็ได้ |

เมื่อผิดกฎเปรียบเทียบราคา error จะมี `loc: ["body"]` และข้อความ `Discount price must be less than regular price` เพราะเป็นข้อผิดพลาดระดับโมเดล ไม่ใช่ `loc: ["body", "discount_price"]` ส่วนราคาลดเป็น 0 จะผิดที่ฟิลด์และมีชื่อ discount_price ใน loc

ลำดับการทำงาน: รับ JSON → ตรวจชนิดและ Field → ตรวจ name ด้วย field_validator → เมื่อทุกฟิลด์ผ่านจึงตรวจสองราคาด้วย model_validator → เรียก endpoint → ส่งผลกลับ

### ตารางทดลองเพิ่มเติม

| สิ่งที่เปลี่ยนจากข้อมูลถูกต้อง | ผลที่ควรเห็น |
|---|---|
| name เป็น `""` | 422: สั้นกว่า min_length |
| price เป็น `0` | 422: gt หมายถึงมากกว่า ไม่รวมเท่ากับ |
| price เป็น `"abc"` | 422: แปลงเป็นตัวเลขไม่ได้ |
| name ยาว 100 ตัวอักษร | 200 |
| name ยาว 101 ตัวอักษร | 422 |
| description ยาว 500 ตัวอักษร | 200 |
| description ยาว 501 ตัวอักษร | 422 |
| description เป็น `null` | 422 เพราะต้องเป็น str |
| ไม่ส่ง description | 200 และใช้ `""` |
| price เป็น `"25"` | 200 เพราะโหมดปกติยอมแปลงข้อความตัวเลขเป็น float |

กรณีสุดท้ายช่วยอธิบายว่า type hint ไม่ได้แปลว่าทุกชนิดที่ต่างกันจะถูกปฏิเสธเสมอ บทนี้ใช้การแปลงชนิดตามค่าเริ่มต้นของ Pydantic ไม่ใช่ strict mode

## 10. หยุดและกลับมารันใหม่

กด **Ctrl+C** ใน Terminal ที่รันเซิร์ฟเวอร์ ครั้งต่อไปเปิดโฟลเดอร์เดิม เลือก `.venv` เปิด terminal ใหม่ แล้วรัน:

```text
fastapi dev main.py
```

- `fastapi` เรียกเครื่องมือ CLI
- `dev` เปิดโหมดพัฒนาและ reload เมื่อบันทึกไฟล์ให้เอง
- `main.py` ระบุไฟล์แอปที่มีตัวแปร `app`

ไม่ต้องสร้าง environment หรือติดตั้งใหม่ทุกครั้ง และไม่ใช้ปุ่ม Run Python File เพื่อเปิด API เพราะปุ่มนั้นไม่ได้สั่งเปิดเซิร์ฟเวอร์

### ทางเลือกตอนส่งงาน: requirements.txt

สร้าง `requirements.txt` ข้าง `main.py` แล้วใส่:

```text
fastapi[standard]
pydantic>=2,<3
```

บรรทัดแรกระบุ FastAPI พร้อมเครื่องมือมาตรฐาน บรรทัดที่สองระบุ Pydantic รุ่น 2 ที่โค้ดใช้ แม้จะติดตั้งตาม FastAPI มาแล้วก็ระบุช่วงรุ่นไว้ได้

ผู้รับงานสร้าง environment ของตัวเองแล้วติดตั้งด้วย:

```text
python -m pip install -r requirements.txt
```

`-r` ให้อ่านรายชื่อจากไฟล์ ส่ง `main.py` และ `requirements.txt` ได้ ไม่ต้องส่ง `.venv`

## 11. ปัญหาที่พบบ่อยใน VS Code

| อาการ | วิธีแก้ |
|---|---|
| ไม่มี Python: Create Environment | ตรวจ Python extension ของ Microsoft |
| ไม่มี Python ให้เลือก | ติดตั้ง Python แล้วเปิด VS Code ใหม่ |
| terminal ใช้ environment เดิม | เลือก interpreter ให้ถูก ปิด terminal เก่า แล้วสร้างใหม่ |
| environment ไม่เปิดใช้หรือ script ถูกบล็อก | เปิด terminal สำหรับ environment จากหน้า Python Environments หากรุ่นที่ใช้รองรับ ให้ค้นหา python-envs.terminal.autoActivationType ใน Settings เลือก shellStartup แล้วเปิด terminal ใหม่ ตรวจให้ได้ True ก่อนติดตั้ง |
| ไม่พบคำสั่ง fastapi | ตรวจ environment และติดตั้ง fastapi[standard] |
| Could not import module main หรือหาไฟล์ไม่เจอ | File → Open Folder เปิดโฟลเดอร์ที่มี main.py แล้วสร้าง terminal ใหม่ อย่าเปิด .venv เป็นโฟลเดอร์หลัก |
| IndentationError | ตรวจย่อหน้า 4/8/12 ช่องและอย่าปน tab กับ space |
| ImportError: field_validator | ตรวจ Pydantic รุ่น 2 และอย่าตั้งชื่อไฟล์ pydantic.py |
| กด Run Python File แล้วไม่มีเว็บ | ใช้ fastapi dev main.py ใน Terminal |
| เปิด /products/validate จาก address bar ได้ 405 | address bar ส่ง GET แต่ API รับ POST ให้ทดลองใน /docs |
| หน้า /docs ไม่โหลด UI | ตรวจอินเทอร์เน็ต เพราะ UI ค่าเริ่มต้นโหลดไฟล์จาก CDN ลองเปิด / เพื่อตรวจว่า API ยังตอบได้ |
| ราคาติดลบยังผ่าน | กด Ctrl+S ตรวจว่ารันไฟล์ที่มี Field(gt=0) |
| พอร์ต 8000 ถูกใช้ | หยุดเซิร์ฟเวอร์เก่าหรือใช้ fastapi dev main.py --port 8001 แล้วเปิด /docs ที่พอร์ต 8001 |


## 12. บทพูดนำเสนอและแบบฝึกหัด

เปิดเรื่อง: “วันนี้จะสร้าง API ตรวจข้อมูลสินค้าจากโฟลเดอร์เปล่า ปัญหาคือราคาที่เป็นตัวเลขอาจยังติดลบได้ เราจะเพิ่มกฎให้เซิร์ฟเวอร์ตรวจเองก่อนนำข้อมูลไปใช้งาน”

ก่อนเพิ่ม Field: “BaseModel ช่วยกำหนดชนิดข้อมูล แต่เราต้องระบุเงื่อนไขทางธุรกิจเพิ่ม เช่น ราคาต้องมากกว่าศูนย์”

ก่อนเพิ่ม validator: “ความยาวหนึ่งตัวอักษรยังอาจเป็นช่องว่าง จึงต้องเขียนกฎตรวจข้อความหลัง strip ด้วย”

ก่อนเพิ่ม model_validator: “ราคาปกติ 100 กับราคาลด 120 ต่างเป็นจำนวนบวก จึงผ่านกฎของแต่ละช่อง แต่เมื่อดูร่วมกันจะผิด เราจึงใช้ model_validator ตรวจความสัมพันธ์ของข้อมูล”

ขณะทดลอง: “ข้อมูลถูกต้องได้ 200 ข้อมูลผิดได้ 422 และ loc บอกว่าเราต้องแก้ฟิลด์ไหน หน้าเว็บจึงนำข้อผิดพลาดไปแสดงข้างช่องกรอกได้”

เพิ่มเติมขณะทดลองสองราคา: “ถ้า loc เป็น body อย่างเดียว แปลว่าเป็นข้อผิดพลาดระดับโมเดล หน้าเว็บอาจแสดงข้อความรวมเหนือฟอร์มได้”

แบบฝึกหัด: เพิ่มกฎให้ราคาต้องไม่เกิน 100000 ด้วย `le=100000` ใน Field ของ price แล้วทดลองราคา 100000 และ 100001 เฉลย: ครั้งแรกผ่าน ครั้งที่สองได้ 422 เพราะ le หมายถึงน้อยกว่าหรือเท่ากับ

เมื่อนำกลับไปใช้กับ web_python66 ให้นำกฎใน Product ไปปรับ schemas ของ product_app โดยรักษาฟิลด์เดิมที่ระบบต้องใช้ เช่น id ส่วนการบันทึกฐานข้อมูลและหน้าเว็บยังใช้โครงสร้างเดิมได้

## 13. ไฟล์ในชุดบทเรียน

- `main.py`: โค้ดฉบับสมบูรณ์สำหรับเทียบหลังฝึก ผู้เรียนเขียนไฟล์นี้ไฟล์เดียว
- `README.md`: คู่มือเต็มตั้งแต่สร้าง environment จนทดลอง API เปิด Preview ใน VS Code ด้วย Ctrl+Shift+V
- `START_HERE.md`: ขั้นเตรียม VS Code แบบย่อสำหรับเปิดประกอบก่อนเริ่มเขียนโค้ด
- `requirements.txt`: รายชื่อแพ็กเกจสำหรับส่งงาน เป็นทางเลือก ไม่ต้องสร้างตอนเริ่มบท
- `instructor/`: เครื่องมือตรวจ ผลตรวจ และรายชื่อรุ่นที่ทดสอบ ผู้เรียนไม่ต้องเขียนหรือรันไฟล์เหล่านี้

โฟลเดอร์เฉลยชื่อ `fastapi_validation_lesson` ส่วนโฟลเดอร์ที่ให้ผู้เรียนเริ่มเองชื่อ `product_validation_demo` ชื่อต่างกันได้ แต่ต้องเปิดโฟลเดอร์ที่มี `main.py` ก่อนรันเสมอ

