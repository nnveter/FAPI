"""Точка входа FastAPI-приложения для КР5."""
from __future__ import annotations

import os

from fastapi import FastAPI

from .routers import admin, rooms, tasks, users
from .schemas import HealthResponse

app = FastAPI(
    title="КР5 — Tasks API + WebSocket Rooms",
    description=(
        "Управление задачами с имитацией авторизации, WebSocket-чат по комнатам "
        "и модульная маршрутизация с внедрением зависимостей."
    ),
    version="1.0.0",
)

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(rooms.http_router)
app.include_router(rooms.ws_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Маршрут проверки состояния приложения."""
    return HealthResponse(status="ok", env=os.getenv("APP_ENV", "local"))
