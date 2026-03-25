from fastapi import FastAPI, Response, Cookie, HTTPException
from typing import Optional
import uuid

app = FastAPI()

sessions: dict[str, dict] = {}

fake_users = {
    "admin": "password123",
    "user1": "secret",
}


@app.post("/login")
def login(username: str, password: str, response: Response):
    if username not in fake_users or fake_users[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_token = str(uuid.uuid4())
    sessions[session_token] = {"username": username}

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=1800,
    )
    return {"message": "Login successful"}


@app.get("/user")
def get_user(session_token: Optional[str] = Cookie(default=None)):
    if session_token is None or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_data = sessions[session_token]
    return {"username": user_data["username"], "message": "Welcome back!"}
