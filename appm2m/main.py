from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import CategoryDB, ProductDB
from .schemas import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductResponse,
)

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


def get_categories_by_ids(category_ids: list[int], db: Session) -> list[CategoryDB]:
    if not category_ids:
        return []
    categories = db.query(CategoryDB).filter(CategoryDB.id.in_(category_ids)).all()
    found_ids = {category.id for category in categories}
    missing_ids = set(category_ids) - found_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category id(s) not found: {sorted(missing_ids)}",
        )
    return categories


# ---------- Categories ----------


@app.post("/categories/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(CategoryDB).filter(CategoryDB.name == category.name).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category.name}' already exists",
        )
    db_category = CategoryDB(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get("/categories/", response_model=list[CategoryResponse])
async def read_categories(db: Session = Depends(get_db)):
    return db.query(CategoryDB).all()


@app.get("/categories/{category_id}", response_model=CategoryResponse)
async def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"detail": "Category deleted"}


# ---------- Products ----------


@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    categories = get_categories_by_ids(product.category_ids, db)
    db_product = ProductDB(
        name=product.name,
        description=product.description,
        price=product.price,
        categories=categories,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/", response_model=list[ProductResponse])
async def read_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()


@app.get("/products/{product_id}", response_model=ProductResponse)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, updated: ProductCreate, db: Session = Depends(get_db)
):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = updated.name
    product.description = updated.description
    product.price = updated.price
    product.categories = get_categories_by_ids(updated.category_ids, db)

    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}
