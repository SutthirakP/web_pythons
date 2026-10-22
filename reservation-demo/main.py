import asyncio  # เพิ่มในช่วงที่ 4: ใช้สร้าง Lock
import secrets  # เพิ่มในช่วงที่ 5: สุ่มรหัสการจอง
import time  # เพิ่มในช่วงที่ 4: ใช้อ่านเวลาจาก monotonic

from fastapi import FastAPI, HTTPException  # ช่วงที่ 1: FastAPI; ช่วงที่ 5: เพิ่ม HTTPException
from pydantic import BaseModel, Field  # เพิ่มในช่วงที่ 2: กำหนดและตรวจข้อมูลรับเข้า

app = FastAPI(title="Last Item Reservation")
RESERVATION_SECONDS = 30
lock = asyncio.Lock()  # เพิ่มในช่วงที่ 4: ทั้งสาม endpoint ใช้ lock ตัวเดียวกัน

product = {
    "id": 1,
    "name": "Limited Sneakers",
    "status": "available",
    "reservation_token": None,
    "expires_at": 0.0,
}


class Confirmation(BaseModel):
    reservation_token: str = Field(min_length=1, max_length=100)


def release_expired_reservation(now: float):
    if product["status"] == "reserved" and now >= product["expires_at"]:
        product["status"] = "available"
        product["reservation_token"] = None
        product["expires_at"] = 0.0


@app.get("/product")
async def get_product():
    async with lock:
        now = time.monotonic()
        release_expired_reservation(now)
        remaining = 0.0
        if product["status"] == "reserved":
            remaining = max(0.0, product["expires_at"] - now)
        return {
            "id": product["id"],
            "name": product["name"],
            "status": product["status"],
            "remaining_seconds": round(remaining, 1),
        }


@app.post("/reserve", status_code=201)
async def reserve_product():
    async with lock:
        now = time.monotonic()
        release_expired_reservation(now)
        if product["status"] != "available":
            raise HTTPException(status_code=409, detail="Product is not available")
        token = secrets.token_urlsafe(24)
        product["status"] = "reserved"
        product["reservation_token"] = token
        product["expires_at"] = now + RESERVATION_SECONDS
        return {
            "message": "Reserved for 30 seconds",
            "reservation_token": token,
            "expires_in": RESERVATION_SECONDS,
        }


@app.post("/confirm")
async def confirm_purchase(data: Confirmation):
    async with lock:
        now = time.monotonic()
        release_expired_reservation(now)
        if product["status"] != "reserved":
            raise HTTPException(status_code=409, detail="No active reservation")
        if data.reservation_token != product["reservation_token"]:
            raise HTTPException(status_code=403, detail="Invalid reservation token")
        product["status"] = "sold"
        product["reservation_token"] = None
        product["expires_at"] = 0.0
        return {"message": "Purchase confirmed", "product_id": product["id"]}