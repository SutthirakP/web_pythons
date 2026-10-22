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
    image: str | None = None  # filename returned by POST /upload


# in — category_ids references existing categories by id (many-to-many via id)
class ProductCreate(Product):
    category_ids: list[int] = []


# out
class ProductResponse(Product):
    id: int
    categories: list[CategoryResponse] = []

    class Config:
        from_attributes = True


# in — plain password here; auth.py hashes it before it ever touches the DB
class UserRegister(BaseModel):
    username: str
    password: str


# out — never include the password/hash in a response
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
