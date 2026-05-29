"""Задание 10.2 — проверка данных запроса и обработка ошибок валидации.

Эндпоинт принимает JSON с данными пользователя и валидирует их моделью
Pydantic. Ошибки валидации перехватываются пользовательским обработчиком
RequestValidationError и возвращаются в едином, информативном формате.
"""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="KR4 — Task 10.2 — Request validation")


class User(BaseModel):
    username: str
    # conint(gt=18) в стиле Pydantic v2 — ограничение через Field.
    age: int = Field(gt=18)
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


class FieldError(BaseModel):
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    success: bool = False
    message: str = "Ошибка валидации входных данных"
    errors: list[FieldError]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Возвращает компактный, читаемый список ошибок по полям."""
    print(f"[ValidationError] {request.url.path}: {exc.errors()}")
    errors = [
        FieldError(
            # Пропускаем префикс 'body'/'query' в loc, оставляя имя поля.
            field=".".join(str(part) for part in err["loc"][1:]) or "__root__",
            message=err["msg"],
        )
        for err in exc.errors()
    ]
    body = ValidationErrorResponse(errors=errors)
    return JSONResponse(status_code=422, content=body.model_dump())


@app.post("/users")
def create_user(user: User):
    # Пароль в ответ не возвращаем.
    return {
        "username": user.username,
        "age": user.age,
        "email": user.email,
        "phone": user.phone,
    }
