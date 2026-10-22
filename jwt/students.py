from fastapi import APIRouter, Depends

from auth import get_current_user

router = APIRouter()

@router.get("/")
async def hello1():
    return {"message": "xxx"}

@router.get("/students")
async def get_students( username: str = Depends(get_current_user)):
    return {
        "message": "Authenticated user",
        "user" : username,
        "students": [
            {"id": 1, "name": "John Doe"},
            {"id": 2, "name": "Jane Smith"}
        ]
    }