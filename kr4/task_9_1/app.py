"""FastAPI-приложение для ресурса Product (Задание 9.1).

Демонстрирует работу со схемой БД, управляемой через Alembic.
Сами изменения схемы выполняются миграциями, а не через create_all.
"""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import get_db
from models import Product

app = FastAPI(title="KR4 — Task 9.1 — Alembic / Product")


class ProductIn(BaseModel):
    title: str
    price: float
    count: int = 0
    description: str


class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
