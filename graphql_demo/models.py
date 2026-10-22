from sqlalchemy import Column, Float, Integer, String

from .database import Base


class ProductDB(Base):
    __tablename__ = "products"
    # sqlite_autoincrement makes SQLite remember the highest id ever used, so when
    # there's no freed id to reuse, a new product always gets a brand-new number.
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)


class FreedIdDB(Base):
    """Ids of deleted products, in the order they were deleted.

    create_product takes the most recently freed id first, so deleting product 3
    and then adding a new one gives the new product id 3.
    """

    __tablename__ = "freed_ids"

    seq = Column(Integer, primary_key=True, autoincrement=True)  # higher = deleted more recently
    product_id = Column(Integer, nullable=False, unique=True)
