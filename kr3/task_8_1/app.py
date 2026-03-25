from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from database import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class User(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(user: User):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user.username, user.password),
    )
    conn.commit()
    conn.close()
    return {"message": "User registered successfully!"}
