from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from .auth import get_current_user
from .auth import router as auth_router
from .chatbot import notify_product_change, product_to_dict
from .chatbot import router as chatbot_router
from .cors import ALLOWED_METHODS, ALLOWED_ORIGINS, MethodCheckingCORSMiddleware
from .cors import router as cors_router
from .upload import delete_image, image_path
from .upload import router as upload_router
from .database import Base, engine, get_db
from .models import CategoryDB, ProductDB
from .rate_limit import connect_redis, redis_is_up
from .streaming import router as streaming_router
from .schemas import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductResponse,
)

def add_missing_columns() -> None:
    with engine.begin() as conn:
        columns = {column["name"] for column in inspect(conn).get_columns("products")}
        if "image" not in columns:
            conn.exec_driver_sql("ALTER TABLE products ADD COLUMN image VARCHAR")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] preparing catalog database...")
    Base.metadata.create_all(bind=engine)
    add_missing_columns()

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    app.state.db_ready = True
    app.state.started_at = datetime.now().isoformat(timespec="seconds")
    print(f"[STARTUP] connected to {engine.url.database}")

    # Redis holds the login rate-limit counters (rate_limit.py). None = not running.
    app.state.redis = await connect_redis()

    try:
        yield
    finally:
        app.state.db_ready = False
        engine.dispose() 
        if app.state.redis is not None:
            await app.state.redis.aclose()
            app.state.redis = None
        print("[SHUTDOWN] database and Redis connections closed")


app = FastAPI(lifespan=lifespan)

# every method except HEAD - see cors.py for why it's a subclass
app.add_middleware(
    MethodCheckingCORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chatbot_router)
app.include_router(upload_router)
app.include_router(cors_router)
app.include_router(streaming_router)


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


def count_products() -> int:
    with engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(ProductDB)).scalar_one()


@app.get("/health")
async def health():
    ready = getattr(app.state, "db_ready", False)
    products = await run_in_threadpool(count_products) if ready else None
    return {
        "status": "online",
        "db_ready": ready,
        "started_at": getattr(app.state, "started_at", None),
        "products": products,
        "redis_ready": await redis_is_up(getattr(app.state, "redis", None)),  # live PING
    }


def check_image(image: str | None) -> None:
    if image is not None and image_path(image) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image '{image}' not found - upload it with POST /upload first",
        )


# ---------- Categories ----------


@app.post("/categories/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
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
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    category = db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"detail": "Category deleted"}


# ---------- Products ----------


@app.post("/products/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    categories = get_categories_by_ids(product.category_ids, db)
    check_image(product.image)
    db_product = ProductDB(
        name=product.name,
        description=product.description,
        price=product.price,
        image=product.image,
        categories=categories,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    await notify_product_change("created", product_to_dict(db_product))
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
    product_id: int,
    updated: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    check_image(updated.image)
    old_image = product.image

    product.name = updated.name
    product.description = updated.description
    product.price = updated.price
    product.image = updated.image
    product.categories = get_categories_by_ids(updated.category_ids, db)

    db.commit()
    db.refresh(product)
    if old_image != product.image:
        delete_image(old_image)  # replaced or removed - don't leave the old file behind
    await notify_product_change("updated", product_to_dict(product))
    return product


@app.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    deleted = product_to_dict(product)  # read it before the row is gone
    db.delete(product)
    db.commit()
    delete_image(deleted["image"])
    await notify_product_change("deleted", deleted)
    return {"detail": "Product deleted"}
