import asyncio
import json

from fastapi import FastAPI, Request,HTTPException,Depends
import redis.asyncio as redis

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.get("/ping")
async def ping():
    return {"redis":await r.ping()}

LIMIT = 5
WINDOW = 60

async def rate_limiter(request: Request):
    ip = request.client.host
    key = f"rate:{ip}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, WINDOW)
    
    if count > LIMIT:
        ttl = await r.ttl(key)
        raise HTTPException(status_code=429,detail=f"ยิงเกิน {LIMIT} ครั้งใน {WINDOW} วินาที. กรุณาลองใหม่อีกครั้งใน {ttl} วินาที.",headers={"Retry-After": str(ttl)})
    return count

@app.get("/hello")
async def  hello(count: int = Depends(rate_limiter)):
    return {"message": "สวัสดี! ","used":count,"remaining":LIMIT - count}

def limiter(limit: int, window: int):
    async def _check(request: Request):
        key = f"rate:{request.url.path}:{request.client.host}"
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window)
        if count > limit:
            ttl = await r.ttl(key)
            raise HTTPException(status_code=429,detail=f"ยิงเกิน {limit} ครั้งใน {window} วินาที. กรุณาลองใหม่อีกครั้งใน {ttl} วินาที.",headers={"Retry-After": str(ttl)})
    return _check

@app.post("/login", dependencies=[Depends(limiter(3, 60))])
async def login():
    return {"message": "ล็อกอินสำเร็จ!"}

@app.get("/products", dependencies=[Depends(limiter(20, 60))])
async def get_products():
    return {"items": ["สินค้า 1", "สินค้า 2", "สินค้า 3"]}

@app.get("/slow-data")
async def slow_data():
    cached = await r.get("cache:slow-data")
    if cached:
        return {"source": "redis cache", "data": json.loads(cached)}
    
    await asyncio.sleep(5)  # Simulate slow processing
    data = {"weather": "sunny", "temperature": 30}
    
    await r.set("cache:slow-data", json.dumps(data), ex=30)
    return {"source": "generated", "data": data}