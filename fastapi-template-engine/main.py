from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
template = Jinja2Templates(directory=BASE_DIR / "templates")

item_db = [
    {"id": 1, "name": "a", "amount": 1},
    {"id": 2, "name": "b", "amount": 2},
    {"id": 3, "name": "c", "amount": 3},
]

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return template.TemplateResponse(request=request, name="index.html", context={"items": item_db})

@app.post("/items", response_class=RedirectResponse)
async def add_item(name: str = Form(...), amount: int = Form(...)):
    next_id = max([item["id"] for item in item_db], default=0) + 1
    item_db.append({"id": next_id, "name": name, "amount": amount})
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    target = next((item for item in item_db if item["id"] == item_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="item not found")

    item_db.remove(target)
    return JSONResponse({"status": "success", "id": item_id})
