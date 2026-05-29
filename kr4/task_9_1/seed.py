"""Наполнение таблицы products двумя записями (шаг 5 задания 9.1).

Запускать после применения миграций:
    python -m alembic upgrade head
    python seed.py
"""
from __future__ import annotations

from database import SessionLocal
from models import Product

SEED_PRODUCTS = [
    Product(title="Keyboard", price=49.99, count=10, description="Mechanical keyboard"),
    Product(title="Mouse", price=19.99, count=25, description="Wireless optical mouse"),
]


def main() -> None:
    db = SessionLocal()
    try:
        if db.query(Product).count() > 0:
            print("Таблица products уже содержит записи — пропускаю seed.")
            return
        db.add_all(SEED_PRODUCTS)
        db.commit()
        for product in db.query(Product).all():
            print(product.id, product.title, product.price, product.count, product.description)
    finally:
        db.close()


if __name__ == "__main__":
    main()
