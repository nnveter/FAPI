"""ORM-модель ресурса Product.

История схемы (отражена в миграциях Alembic):
  * Миграция 0001 — создаёт таблицу с полями id, title, price, count.
  * Миграция 0002 — добавляет NOT NULL поле description.

Текущее состояние модели соответствует последней миграции (0002).
"""
from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Поле добавлено во второй миграции, обязательно (NOT NULL).
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
