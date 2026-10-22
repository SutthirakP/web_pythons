from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator, model_validator

app = FastAPI(title="Product Validation Demo")


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, allow_inf_nan=False)
    description: str = Field(default="", max_length=500)
    discount_price: float | None = Field(default=None, gt=0, allow_inf_nan=False)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_name = value.strip()
        if not cleaned_name:
            raise ValueError("Product name must not be blank")
        return cleaned_name

    @model_validator(mode="after")
    def validate_discount(self) -> "Product":
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("Discount price must be less than regular price")
        return self


@app.get("/")
def home():
    return {"message": "API is ready"}


@app.post("/products/validate")
def validate_product(product: Product):
    return {"message": "Product is valid", "product": product.model_dump()}
