"""Задание 10.1 — пользовательская обработка ошибок в FastAPI.

Содержит:
  * пользовательские классы исключений (CustomExceptionA, CustomExceptionB);
  * обработчики этих исключений (@app.exception_handler);
  * Pydantic-модель формата ответа об ошибке (единый envelope);
  * эндпоинты, которые порождают исключения в определённых сценариях.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="KR4 — Task 10.1 — Custom error handling")


# --- Пользовательские исключения --------------------------------------------

class CustomExceptionA(Exception):
    """Бизнес-правило нарушено. Уникальный код состояния 418."""

    status_code = 418
    error_code = "CONDITION_NOT_MET"

    def __init__(self, message: str = "Условие не выполнено") -> None:
        self.message = message
        super().__init__(message)


class CustomExceptionB(Exception):
    """Ресурс не найден. Уникальный код состояния 404."""

    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"

    def __init__(self, message: str = "Ресурс не найден") -> None:
        self.message = message
        super().__init__(message)


# --- Модель ответа об ошибке (единый формат) ---------------------------------

class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str


# --- Обработчики исключений ---------------------------------------------------

@app.exception_handler(CustomExceptionA)
async def handle_custom_exception_a(request: Request, exc: CustomExceptionA) -> JSONResponse:
    # В реальном приложении здесь было бы logging.error(...). Для задания — print.
    print(f"[CustomExceptionA] {request.url.path}: {exc.message}")
    body = ErrorResponse(error_code=exc.error_code, message=exc.message)
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(CustomExceptionB)
async def handle_custom_exception_b(request: Request, exc: CustomExceptionB) -> JSONResponse:
    print(f"[CustomExceptionB] {request.url.path}: {exc.message}")
    body = ErrorResponse(error_code=exc.error_code, message=exc.message)
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


# --- Эндпоинты ----------------------------------------------------------------

# Простое in-memory "хранилище" товаров для демонстрации сценария "не найдено".
_ITEMS: dict[int, str] = {1: "apple", 2: "banana"}


@app.get("/divide")
def divide(a: float, b: float):
    """Сценарий CustomExceptionA: деление на ноль запрещено бизнес-правилом."""
    if b == 0:
        raise CustomExceptionA(message="Делить на ноль нельзя")
    return {"result": a / b}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Сценарий CustomExceptionB: запрошенный ресурс отсутствует."""
    if item_id not in _ITEMS:
        raise CustomExceptionB(message=f"Товар с id={item_id} не найден")
    return {"id": item_id, "name": _ITEMS[item_id]}
