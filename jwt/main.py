from  fastapi import FastAPI
from students import router as students_router
from auth import router as auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(students_router)
