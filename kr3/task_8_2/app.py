from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, int(todo.completed)),
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    result = dict(row)
    result["completed"] = bool(result["completed"])
    return result


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    updated = dict(existing)
    if todo.title is not None:
        updated["title"] = todo.title
    if todo.description is not None:
        updated["description"] = todo.description
    if todo.completed is not None:
        updated["completed"] = int(todo.completed)

    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (updated["title"], updated["description"], updated["completed"], todo_id),
    )
    conn.commit()
    conn.close()
    updated["completed"] = bool(updated["completed"])
    return updated


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": f"Todo {todo_id} deleted successfully"}
