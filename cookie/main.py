from fastapi import FastAPI, HTTPException, Response,Cookie
from typing import Annotated
import secrets
from pydantic import BaseModel, Field

app = FastAPI()
sessions: dict[str, str] = {}

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

class NameIn(BaseModel):
    name : str = Field(min_length=2, max_length=100)

@app.post("/set-name")
def set_name(body: NameIn, response: Response):
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = body.name
    response.set_cookie(key="session_id", value=session_id,max_age=3600,httponly=True)
    return {"message": f'remembered: {body.name}!'}

@app.get("/welcome")
def welcome(session_id: Annotated[str | None, Cookie()] = None):
    name = sessions.get(session_id)
    if name is None:
        raise HTTPException(status_code=401, detail="don't know you yet!")
    return {"message": f"welcome back, {name}!"}

@app.post("/forget")
def forget(response: Response, session_id: Annotated[str | None, Cookie()] = None):
    sessions.pop(session_id, None)
    response.delete_cookie(key="session_id")
    return {"message": "cookie forgotten!"}