from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# next to this file, so it works no matter where the server is started from
sqlite_file_name = Path(__file__).resolve().parent / "product.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Data model (table)
class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)


# in — fields needed to create a product (no id, DB generates it)
class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


# in — same fields, used for full update via PUT
class ProductUpdate(BaseModel):
    name: str
    description: str | None = None
    price: float


# out
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float

    class Config:
        from_attributes = True


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# CREATE
@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductDB(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# READ (all)
@app.get("/products/", response_model=list[ProductResponse])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(ProductDB).offset(skip).limit(limit).all()
    return products


# READ (one)
@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return product


# UPDATE
@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, updated: ProductUpdate, db: Session = Depends(get_db)
):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    for field, value in updated.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


# DELETE
@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    db.delete(product)
    db.commit()
    return {"message": "Deleted product successfully", "data": product}
