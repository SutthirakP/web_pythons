from typing import List, Optional

import strawberry

from .database import SessionLocal
from .models import FreedIdDB, ProductDB


def reuse_product_id(db) -> Optional[int]:
    """Pick the id a new product should reuse, or None to let the DB assign a new one.

    1. the most recently deleted id (tracked in freed_ids)
    2. otherwise the smallest gap in the ids still in use (covers deletions made
       before freed_ids existed)
    """
    used = {row_id for (row_id,) in db.query(ProductDB.id)}

    for freed in db.query(FreedIdDB).order_by(FreedIdDB.seq.desc()):
        db.delete(freed)  # handed out now (or already taken), so it's no longer free
        if freed.product_id not in used:
            return freed.product_id

    gap = next((n for n in range(1, max(used, default=0)) if n not in used), None)
    return gap


@strawberry.type
class Product:
    id: int
    name: str
    price: float

    @classmethod
    def from_db(cls, product: ProductDB) -> "Product":
        return cls(id=product.id, name=product.name, price=product.price)

@strawberry.type
class Query:
    @strawberry.field
    def product(self, id: int) -> Optional[Product]:
        with SessionLocal() as db:
            row = db.get(ProductDB, id)
            return Product.from_db(row) if row else None

    @strawberry.field
    def products(self) -> List[Product]:
        with SessionLocal() as db:
            return [Product.from_db(row) for row in db.query(ProductDB).order_by(ProductDB.id).all()]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(self, name: str, price: float) -> Product:
        with SessionLocal() as db:
            row = ProductDB(id=reuse_product_id(db), name=name, price=price)  # id=None -> DB assigns a new one
            db.add(row)
            db.commit()
            db.refresh(row)
            return Product.from_db(row)

    @strawberry.mutation
    def update_product(
        self, id: int, name: Optional[str] = None, price: Optional[float] = None
    ) -> Optional[Product]:
        with SessionLocal() as db:
            row = db.get(ProductDB, id)
            if row is None:
                return None
            if name is not None:
                row.name = name
            if price is not None:
                row.price = price
            db.commit()
            db.refresh(row)
            return Product.from_db(row)

    @strawberry.mutation
    def delete_product(self, id: int) -> bool:
        with SessionLocal() as db:
            row = db.get(ProductDB, id)
            if row is None:
                return False
            db.delete(row)
            db.add(FreedIdDB(product_id=id))  # remember it so the next create reuses it
            db.commit()
            return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
