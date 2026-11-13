"""Streaming homework: write a product description and stream it word by word (SSE).

GET /products/{id}/describe  ->  text/event-stream

    event: start   data: {"product_id": 1, "words": 42}
    event: token   data: "Meet "            (one per word)
    event: token   data: "the "
    ...
    event: done    data: {"text": "<the whole description>"}

The page reads it with the browser's EventSource and shows each word as it
arrives, like a chat AI typing. The text is built from the product's own data
(name, categories, price) - there is no real AI model behind it.
"""

import asyncio
import random
import re
from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.sse import EventSourceResponse, ServerSentEvent
from sqlalchemy.orm import Session

from .database import get_db
from .models import ProductDB

router = APIRouter(tags=["streaming"])

WORD_DELAY = 0.06  # seconds between words - slow enough to watch it stream
THINKING_DELAY = 0.6  # pause before the first word, like a model "thinking"


def get_product_info(product_id: int, db: Annotated[Session, Depends(get_db)]) -> dict:
    # Runs BEFORE the stream starts, so a missing product is still a normal 404.
    # Copies the fields into a dict so nothing touches the DB session mid-stream.
    product = db.get(ProductDB, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "categories": [category.name for category in product.categories],
    }


def write_description(product: dict) -> str:
    rng = random.Random()  # new wording every click
    name = product["name"]
    price = product["price"]
    categories = product["categories"]

    opener = rng.choice([
        f"Meet the {name}.",
        f"Say hello to the {name}.",
        f"Upgrade your setup with the {name}.",
    ])

    if categories:
        joined = " and ".join(categories)
        fit = rng.choice([
            f"A standout pick in our {joined} range,",
            f"Hand-picked for the {joined} collection,",
        ])
    else:
        fit = rng.choice(["A versatile everyday essential,", "Simple, reliable and ready to go,"])

    body = rng.choice([
        "it is built to make daily tasks faster and easier.",
        "it combines solid build quality with a clean, modern design.",
        "it does exactly what you need without getting in the way.",
    ])

    if price < 50:
        value = f"At just ${price:,.2f}, it is an easy add-to-cart."
    elif price < 500:
        value = f"For ${price:,.2f}, you get great value without compromise."
    else:
        value = f"At ${price:,.2f}, it is a premium choice that is worth every cent."

    closer = rng.choice([
        "Order today while stock lasts!",
        "Grab yours before it sells out!",
        "Add it to your cart now!",
    ])
    return f"{opener} {fit} {body} {value} {closer}"


@router.get("/products/{product_id}/describe", response_class=EventSourceResponse)
async def stream_description(
    product: Annotated[dict, Depends(get_product_info)],
) -> AsyncIterable[ServerSentEvent]:
    text = write_description(product)
    words = re.findall(r"\S+\s*", text)  # keep the space after each word

    yield ServerSentEvent(data={"product_id": product["id"], "words": len(words)}, event="start")
    await asyncio.sleep(THINKING_DELAY)

    for word in words:
        yield ServerSentEvent(data=word, event="token")
        await asyncio.sleep(WORD_DELAY)

    yield ServerSentEvent(data={"text": text}, event="done")
