# การบ้าน CORS (ห้าม HEAD) + Streaming — appm2m (Catalog)

| การบ้าน | ส่ง | ไฟล์ |
|---|---|---|
| `@app.head("/foo")` + ตั้ง CORS ให้ทุก method ยกเว้น HEAD + ปุ่มที่กดแล้วเห็น CORS error | 30 Oct | [cors.py](cors.py), `frontend/src/app/catalog/CorsLab.tsx` |
| ใส่ streaming ในโปรเจกต์ตามไอเดียตัวเอง | 11 Nov | [streaming.py](streaming.py), `frontend/src/app/catalog/DescribeStream.tsx` |

---

## เปิดก่อนโชว์

```powershell
uv run python run_all.py         # backend (Catalog อยู่พอร์ต 8002) + เปิด Redis ให้
cd frontend; npm run dev         # อีก terminal
```

เปิด **http://localhost:3000/catalog** แล้วกด **F12** เปิดแท็บ **Console** ค้างไว้

---

## การบ้าน 1 — CORS ห้าม HEAD

### โชว์ยังไง

1. เลื่อนลงไปการ์ด **CORS test** (คอลัมน์ซ้ายล่างสุด)
2. กด **Send HEAD /foo** → ขึ้นกล่อง **แดง**
   ```
   ✕ HEAD  Blocked by CORS policy — TypeError: Failed to fetch. The HEAD method is not allowed for this origin.
   ```
   และใน Console ของเบราว์เซอร์จะขึ้นข้อความตัวจริง:
   ```
   Access to fetch at 'http://localhost:8002/foo' from origin 'http://localhost:3000' has been blocked by CORS policy:
   No 'Access-Control-Allow-Origin' header is present on the requested resource.
   ```
3. กด **Send GET /foo** (URL เดียวกัน แค่เปลี่ยน method) → ขึ้นกล่อง **เขียว** `200 OK — {"message":"GET /foo is allowed by CORS"}`

→ พิสูจน์ว่าบล็อกเพราะ **method** ไม่ใช่เพราะ URL หรือ server ล่ม

### โค้ดที่ใช้ ([cors.py](cors.py))

```python
ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]   # ทุกตัวยกเว้น HEAD

@router.head("/foo")
def head_foo() -> Response:
    return Response(headers={"X-Foo": "hello from HEAD"})
```

และใน [main.py](main.py):

```python
app.add_middleware(
    MethodCheckingCORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=ALLOWED_METHODS,
    ...
)
```

### จุดที่ต้องอธิบายได้ (อาจารย์ถามแน่)

**ทำไมต้องเขียน `MethodCheckingCORSMiddleware` เพิ่ม ใช้ `CORSMiddleware` ธรรมดาไม่ได้เหรอ?**

ใช้ไม่ได้ เพราะ **HEAD เป็น "simple request"** (เหมือน GET กับ POST ธรรมดา) เบราว์เซอร์จะ **ไม่ส่ง preflight (OPTIONS) มาถามก่อน** แต่ยิง HEAD ไปเลย

ส่วน `CORSMiddleware` ของ Starlette เช็ค `allow_methods` **เฉพาะตอน preflight** — ถ้าไม่มี preflight มันก็แปะ `Access-Control-Allow-Origin` ให้ทุก method → HEAD ผ่าน ไม่มี error

ตัว subclass เลยเพิ่มการเช็ค method ตอน request ปกติด้วย: method ไหนไม่อยู่ในรายการ → **ไม่ใส่ header CORS** → เบราว์เซอร์บล็อก

| request | ใครเช็ค | ผล |
|---|---|---|
| `OPTIONS` + `Access-Control-Request-Method: HEAD` (preflight) | CORSMiddleware เดิม | 400 `Disallowed CORS method` |
| `HEAD` ตรง ๆ (simple request — กรณีปุ่มบนหน้าเว็บ) | ส่วนที่เขียนเพิ่ม | 200 แต่ **ไม่มี** `Access-Control-Allow-Origin` → เบราว์เซอร์บล็อก |
| `GET` | ปกติ | 200 + มี `Access-Control-Allow-Origin` → ผ่าน |

**CORS ป้องกันใคร?** — เป็นกฎของ **เบราว์เซอร์** เท่านั้น
- ดูที่ terminal ของ backend ตอนกด HEAD จะเห็น `"HEAD /foo HTTP/1.1" 200 OK` = **server ได้รับและตอบแล้ว** แต่เบราว์เซอร์ไม่ยอมส่งผลให้หน้าเว็บ
- ยิงจาก `/docs` หรือ curl ได้ปกติ เพราะไม่ใช่การเรียกข้าม origin จากหน้าเว็บ:
  ```powershell
  curl.exe -I http://localhost:8002/foo        # -I = HEAD → 200, มี X-Foo
  ```

**ทำไมหน้าเว็บได้แค่ `TypeError: Failed to fetch`?** — เบราว์เซอร์ตั้งใจซ่อนเหตุผลจาก JavaScript (กันเว็บร้ายสอดแนม) ข้อความเต็มดูได้ใน Console เท่านั้น

---

## การบ้าน 2 — Streaming: ✨ เขียนคำอธิบายสินค้า

### ไอเดีย

ปุ่ม ✨ ข้างสินค้าแต่ละตัว → server "เขียน" คำอธิบายสินค้าจากชื่อ หมวด และราคา แล้ว **ส่งมาทีละคำ** ด้วย Server-Sent Events (SSE) หน้าเว็บโชว์คำที่พิมพ์ออกมาเรื่อย ๆ เหมือน ChatGPT พอพอใจกด **Use as description** บันทึกลงสินค้าได้เลย

### โชว์ยังไง

1. **Log in** ก่อน (ถ้าจะบันทึก — ดูการสตรีมเฉย ๆ ไม่ต้อง login)
2. กด **✨** ที่สินค้าตัวไหนก็ได้ จะเห็นตามลำดับ:
   - `✨ Thinking…` + จุดเด้ง (server หยุดคิด 0.6 วินาที)
   - `✨ Writing… 7/32 words` ข้อความโผล่ทีละคำ มีเคอร์เซอร์กระพริบ + แถบความคืบหน้า
   - `✨ Done · 32 words` และมุมขวาบอกเวลา เช่น **`first word 623 ms · all 2371 ms`**
3. กด **Use as description** → คำอธิบายใต้ชื่อสินค้าเปลี่ยนทันที
4. ลอง **↻ Regenerate** ได้ข้อความใหม่ทุกครั้ง, **Stop** หยุดกลางทาง

**ประโยคเด็ดตอนนำเสนอ:** ดูตัวเลข `first word 623 ms · all 2371 ms` — ถ้าไม่ stream ผู้ใช้ต้องจ้องจอว่าง ๆ 2.4 วินาที แต่ stream แล้วเห็นคำแรกตั้งแต่ 0.6 วินาที **เวลารวมเท่าเดิม แต่รู้สึกเร็วขึ้นมาก**

### ดูของจริงที่วิ่งในสาย

- **DevTools → Network** → คลิก request `describe` → แท็บ **EventStream** จะเห็นแต่ละ event ไหลเข้ามา
- หรือยิงด้วย curl (`-N` = ไม่ buffer):
  ```powershell
  curl.exe -N http://127.0.0.1:8002/products/1/describe
  ```
  ```
  event: start
  data: {"product_id": 1, "words": 32}

  event: token
  data: "Meet "

  event: token
  data: "the "
  ...
  event: done
  data: {"text": "Meet the ..."}
  ```

### โค้ด

ฝั่ง server ([streaming.py](streaming.py)) — ใช้ `EventSourceResponse` + `yield` ของ FastAPI:

```python
@router.get("/products/{product_id}/describe", response_class=EventSourceResponse)
async def stream_description(product: Annotated[dict, Depends(get_product_info)]):
    text = write_description(product)
    words = re.findall(r"\S+\s*", text)

    yield ServerSentEvent(data={"product_id": product["id"], "words": len(words)}, event="start")
    await asyncio.sleep(THINKING_DELAY)
    for word in words:
        yield ServerSentEvent(data=word, event="token")    # ส่งออกไปทันที ไม่รอจบ
        await asyncio.sleep(WORD_DELAY)
    yield ServerSentEvent(data={"text": text}, event="done")
```

- `get_product_info` เป็น dependency → รัน **ก่อน** เริ่ม stream สินค้าไม่มีเลยยังตอบ **404** ปกติได้ (ถ้าเริ่ม stream ไปแล้วจะเปลี่ยน status code ไม่ได้)

ฝั่งหน้าเว็บ (`DescribeStream.tsx`) — ใช้ `EventSource` ของเบราว์เซอร์:

```ts
const source = new EventSource(`${apiUrl}/products/${productId}/describe`);
source.addEventListener("token", (e) => setText((t) => t + JSON.parse(e.data)));
source.addEventListener("done", () => source.close());   // ต้องปิดเอง ไม่งั้น EventSource ต่อใหม่วนไป
```

### SSE ต่างจาก WebSocket (แชทบอท) ยังไง

| | SSE (✨ คำอธิบาย) | WebSocket (แชทบอท) |
|---|---|---|
| ทิศทาง | server → client ทางเดียว | สองทาง |
| โปรโตคอล | HTTP ธรรมดา (`text/event-stream`) | อัปเกรดเป็น `ws://` |
| ฝั่งเบราว์เซอร์ | `EventSource` | `WebSocket` |
| เหมาะกับ | ส่งผลลัพธ์ยาว ๆ ทีละส่วน, แจ้งเตือน | แชท, เกม, ส่งไปมาตลอด |

---

## Test

```powershell
uv run pytest appm2m -v      # 28 passed (เพิ่ม 7 test)
```

| Test | เช็คอะไร |
|---|---|
| `test_head_foo_works_without_browser` | ไม่มี `Origin` (เหมือน curl) → HEAD ได้ 200 + header `X-Foo` |
| `test_head_foo_gets_no_cors_header` | HEAD จากหน้าเว็บ → server ตอบ 200 แต่ **ไม่มี** `Access-Control-Allow-Origin` |
| `test_get_foo_gets_cors_header` | GET จากหน้าเว็บ → มี `Access-Control-Allow-Origin` |
| `test_preflight_rejects_head` | preflight ขอ HEAD → 400 |
| `test_preflight_allows_other_methods` | GET/POST/PUT/PATCH/DELETE ผ่าน preflight |
| `test_describe_streams_word_by_word` | ได้ `text/event-stream`, เริ่ม `start` จบ `done`, token หลายชิ้นต่อกันได้ข้อความเต็ม |
| `test_describe_missing_product_is_404` | สินค้าไม่มี → 404 |
