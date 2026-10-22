from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from .database import Base, SessionLocal, engine
from .models import ProductDB
from .schema import schema

Base.metadata.create_all(bind=engine)

# Seed the two starter products once, only if the table is empty
with SessionLocal() as db:
    if db.query(ProductDB).count() == 0:
        db.add_all([
            ProductDB(name="Iphone", price=67),
            ProductDB(name="IPAD", price=69420),
        ])
        db.commit()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(GraphQLRouter(schema), prefix="/graphql")
