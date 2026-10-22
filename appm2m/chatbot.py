"""Catalog chatbot over WebSocket.

One connection per open chat window, kept open the whole time, so the server can:
  - stream a reply word by word (many small frames instead of one HTTP response)
  - push messages the user never asked for: product added/edited/deleted by
    someone else, and how many people are online right now

Frames are JSON, always with a "type":

  client -> server
    {"type": "message", "text": "..."}
    {"type": "ping", "sent": <ms>}              latency check

  server -> client
    {"type": "welcome", "text", "suggestions"}
    {"type": "typing"}
    {"type": "start", "id"}
    {"type": "delta", "id", "text"}             piece of the reply
    {"type": "end", "id", "products", "suggestions"}
    {"type": "notify", "event", "text", "product"}   broadcast to everyone
    {"type": "presence", "online"}               broadcast to everyone
    {"type": "pong", "sent"}
"""

import asyncio
import re

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from .database import SessionLocal
from .models import CategoryDB, ProductDB

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.add(websocket)
        await self.broadcast({"type": "presence", "online": len(self.active)})

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active.discard(websocket)
        await self.broadcast({"type": "presence", "online": len(self.active)})

    async def broadcast(self, message: dict) -> None:
        for websocket in list(self.active):
            try:
                await websocket.send_json(message)
            except Exception:
                self.active.discard(websocket)  # closed without a clean disconnect


manager = ConnectionManager()


def product_to_dict(product: ProductDB) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image": product.image,
        "categories": [category.name for category in product.categories],
    }


async def notify_product_change(event: str, product: dict) -> None:
    """Called by the REST endpoints in main.py after a product changes."""
    texts = {
        "created": f"🆕 มีสินค้าใหม่: {product['name']} ราคา {format_price(product['price'])}",
        "updated": f"✏️ อัปเดตสินค้า: {product['name']} ราคา {format_price(product['price'])}",
        "deleted": f"🗑 ลบสินค้า: {product['name']} ออกจากร้านแล้ว",
    }
    await manager.broadcast(
        {"type": "notify", "event": event, "text": texts[event], "product": product}
    )


# ---------- the bot's "brain" ----------

GREETINGS = ("สวัสดี", "หวัดดี", "hello", "hi", "hey")
# \b only on the English words: Thai has no spaces, so "สวัสดีครับ" must still match
GREETING_PATTERN = re.compile(r"^(?:สวัสดี|หวัดดี|(?:hello|hi|hey)\b)")
HELP_WORDS = ("ช่วย", "ทำอะไรได้", "help", "คุณคือ")
CHEAP_WORDS = ("ถูกที่สุด", "ถูกสุด", "cheapest", "ราคาต่ำสุด")
EXPENSIVE_WORDS = ("แพงที่สุด", "แพงสุด", "most expensive", "ราคาสูงสุด")
COUNT_WORDS = ("กี่ชิ้น", "กี่อย่าง", "จำนวน", "how many")
CATEGORY_WORDS = ("หมวด", "ประเภท", "category", "categories")
ALL_WORDS = ("ทั้งหมด", "มีอะไรขาย", "all products", "list")
BUDGET_PATTERN = re.compile(r"(?:ไม่เกิน|งบ|under|below|<=?)\s*([\d,]+(?:\.\d+)?)")
# words that don't help find a product by name: "ราคา USB HUB" -> "usb hub"
FILLER_PATTERN = re.compile(
    r"ราคา|รายละเอียด|ข้อมูล|สินค้า|ขอดู|ดู|มี|ไหม|มั้ย|ค้นหา|หา|ครับ|ค่ะ|คะ|\?|\b(?:price|of|search)\b"
)


def format_price(price: float) -> str:
    return f"${price:,.2f}"  # same format as the catalog page


def suggestions_for(products: list[ProductDB], categories: list[CategoryDB]) -> list[str]:
    tips = ["สินค้าทั้งหมด", "สินค้าที่ถูกที่สุด"]
    if products:
        tips.append(f"ราคา {products[0].name}")
        tips.append(f"งบไม่เกิน {int(max(p.price for p in products))}")
    if categories:
        tips.append(f"สินค้าหมวด {categories[0].name}")
    else:
        tips.append("หมวดหมู่ทั้งหมด")
    tips.append("มีสินค้ากี่ชิ้น")
    return tips


def answer(text: str) -> dict:
    """Pick a reply for one user message. Plain sync DB code, so it runs in a thread."""
    query = text.strip().lower()

    with SessionLocal() as db:
        products = db.query(ProductDB).order_by(ProductDB.price).all()
        categories = db.query(CategoryDB).order_by(CategoryDB.name).all()
        tips = suggestions_for(products, categories)

        def reply(message: str, found: list[ProductDB] | None = None) -> dict:
            return {
                "text": message,
                "products": [product_to_dict(p) for p in found or []],
                "suggestions": tips,
            }

        if not products and not any(word in query for word in GREETINGS + HELP_WORDS):
            return reply("ตอนนี้ร้านยังไม่มีสินค้าเลย 😅 ลอง login แล้วเพิ่มสินค้าในหน้า Catalog ก่อนนะ")

        if GREETING_PATTERN.match(query):
            return reply("สวัสดีครับ 👋 อยากดูสินค้าตัวไหน หรือมีงบเท่าไหร่ บอกได้เลย")

        if any(word in query for word in CHEAP_WORDS):
            cheapest = products[0]
            return reply(f"ตัวที่ถูกที่สุดคือ {cheapest.name} ราคา {format_price(cheapest.price)}", [cheapest])

        if any(word in query for word in EXPENSIVE_WORDS):
            priciest = products[-1]
            return reply(f"ตัวที่แพงที่สุดคือ {priciest.name} ราคา {format_price(priciest.price)}", [priciest])

        budget = BUDGET_PATTERN.search(query)
        if budget:
            limit = float(budget.group(1).replace(",", ""))
            within = [p for p in products if p.price <= limit]
            if not within:
                return reply(f"ไม่มีสินค้าที่ราคาไม่เกิน {format_price(limit)} เลย ตัวที่ถูกสุดคือ {products[0].name} ({format_price(products[0].price)})")
            return reply(f"สินค้าที่ราคาไม่เกิน {format_price(limit)} มี {len(within)} ชิ้น", within)

        if any(word in query for word in COUNT_WORDS):
            return reply(f"ตอนนี้มีสินค้า {len(products)} ชิ้น ใน {len(categories)} หมวดหมู่")

        for category in categories:
            if category.name.lower() in query:
                found = sorted(category.products, key=lambda p: p.price)
                if not found:
                    return reply(f"หมวด {category.name} ยังไม่มีสินค้าเลย")
                return reply(f"หมวด {category.name} มีสินค้า {len(found)} ชิ้น", found)

        if any(word in query for word in CATEGORY_WORDS):
            if not categories:
                return reply("ยังไม่มีหมวดหมู่เลย")
            names = ", ".join(f"{c.name} ({len(c.products)})" for c in categories)
            return reply(f"มีทั้งหมด {len(categories)} หมวด: {names}")

        if any(word in query for word in ALL_WORDS):
            return reply(f"ตอนนี้มีสินค้าทั้งหมด {len(products)} ชิ้น เรียงจากถูกไปแพง", products)

        if any(word in query for word in HELP_WORDS):
            return reply(
                "ผมช่วยได้ประมาณนี้ครับ: ดูสินค้าทั้งหมด, หาตัวที่ถูก/แพงที่สุด, "
                "ดูราคาสินค้าตามชื่อ, หาสินค้าตามงบ (เช่น \"งบไม่เกิน 500\"), ดูสินค้าตามหมวดหมู่ "
                "และถ้ามีคนเพิ่ม/แก้/ลบสินค้า ผมจะเด้งบอกทันทีเลย"
            )

        keyword = FILLER_PATTERN.sub(" ", query).strip()
        if keyword:
            found = [
                p for p in products
                if keyword in p.name.lower() or keyword in (p.description or "").lower()
            ]
            if len(found) == 1:
                p = found[0]
                categories_text = ", ".join(c.name for c in p.categories) or "ไม่มีหมวด"
                detail = f" — {p.description}" if p.description else ""
                return reply(f"{p.name} ราคา {format_price(p.price)}{detail} (หมวด: {categories_text})", found)
            if found:
                return reply(f"เจอสินค้าที่ตรงกับ \"{keyword}\" {len(found)} ชิ้น", found)

        return reply("ขอโทษครับ ยังไม่เข้าใจ 🙏 ลองกดคำแนะนำด้านล่าง หรือพิมพ์ชื่อสินค้าดูได้เลย")


# ---------- the WebSocket endpoint ----------


async def stream_reply(websocket: WebSocket, message_id: int, result: dict) -> None:
    await websocket.send_json({"type": "start", "id": message_id})
    for word in re.findall(r"\S+\s*", result["text"]):
        await websocket.send_json({"type": "delta", "id": message_id, "text": word})
        await asyncio.sleep(0.035)
    await websocket.send_json(
        {
            "type": "end",
            "id": message_id,
            "products": result["products"],
            "suggestions": result["suggestions"],
        }
    )


@router.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        welcome = await run_in_threadpool(answer, "help")
        await websocket.send_json(
            {
                "type": "welcome",
                "text": "สวัสดีครับ 👋 มีอะไรให้ช่วยมั้ย? ถามเรื่องสินค้า ราคา หรือหมวดหมู่ได้เลย",
                "suggestions": welcome["suggestions"],
            }
        )

        message_id = 0
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "sent": data.get("sent")})
                continue

            text = str(data.get("text", "")).strip()
            if data.get("type") != "message" or not text:
                continue

            message_id += 1
            await websocket.send_json({"type": "typing"})
            result = await run_in_threadpool(answer, text[:500])
            await asyncio.sleep(0.4)  # a short "thinking" pause so the typing dots are visible
            await stream_reply(websocket, message_id, result)
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)
