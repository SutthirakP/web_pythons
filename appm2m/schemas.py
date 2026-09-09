from pydantic import BaseModel


class Category(BaseModel):
    name: str


# in
class CategoryCreate(Category):
    pass


# out
class CategoryResponse(Category):
    id: int

    class Config:
        from_attributes = True


class Product(BaseModel):
    name: str
    description: str | None = None
    price: float


# in — category_ids references existing categories by id (many-to-many via id)
class ProductCreate(Product):
    category_ids: list[int] = []


# out
class ProductResponse(Product):
    id: int
    categories: list[CategoryResponse] = []

    class Config:
        from_attributes = True
