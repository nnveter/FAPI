"""Задание 11.1 — приложение FastAPI с несколькими эндпоинтами.

Простое in-memory хранилище задач (todo) с CRUD-эндпоинтами.
Модульные тесты к этому приложению — в test_app.py (pytest + TestClient).
"""
from __future__ import annotations

from itertools import count

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI(title="KR4 — Task 11.1 — Unit tests")

_db: dict[int, dict] = {}
_id_seq = count(start=1)


class TodoIn(BaseModel):
    title: str = Field(min_length=1)
    done: bool = False


class TodoOut(TodoIn):
    id: int


def reset_state() -> None:
    """Сброс состояния хранилища (используется в тестах для изоляции)."""
    global _id_seq
    _db.clear()
    _id_seq = count(start=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(todo: TodoIn):
    todo_id = next(_id_seq)
    _db[todo_id] = todo.model_dump()
    return {"id": todo_id, **_db[todo_id]}


@app.get("/todos", response_model=list[TodoOut])
def list_todos():
    return [{"id": tid, **data} for tid, data in _db.items()]


@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int):
    if todo_id not in _db:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"id": todo_id, **_db[todo_id]}


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    if _db.pop(todo_id, None) is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return Response(status_code=204)
