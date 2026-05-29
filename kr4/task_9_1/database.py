"""Настройка подключения к базе данных (SQLAlchemy 2.0)."""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# По умолчанию используется локальный SQLite-файл. URL можно переопределить
# через переменную окружения DATABASE_URL (см. .env.example).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./products.db")

# check_same_thread нужен только для SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""


def get_db():
    """FastAPI-зависимость: выдаёт сессию и гарантированно её закрывает."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
