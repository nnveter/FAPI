from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Laptop",       "category": "electronics", "price": 999.99},
    {"id": 2, "name": "Smartphone",   "category": "electronics", "price": 499.99},
    {"id": 3, "name": "T-Shirt",      "category": "clothing",    "price": 19.99},
    {"id": 4, "name": "Jeans",        "category": "clothing",    "price": 49.99},
    {"id": 5, "name": "Coffee Maker", "category": "appliances",  "price": 79.99},
]

# NOTE: /products/search must be defined BEFORE /product/{product_id}
# to prevent FastAPI from treating "search" as a product_id integer.
@app.get("/products/search")
def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10,
):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
        and (category is None or p["category"] == category)
    ]
    return {"results": results[:limit], "total": len(results)}


@app.get("/product/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
