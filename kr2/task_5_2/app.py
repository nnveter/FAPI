from fastapi import FastAPI, Response, Cookie, HTTPException
from typing import Optional
import uuid
from itsdangerous import URLSafeSerializer, BadSignature

app = FastAPI()

SECRET_KEY = "super-secret-key-change-in-production"
serializer = URLSafeSerializer(SECRET_KEY)

fake_users = {
    "admin": "password123",
    "user1": "secret",
}


@app.post("/login")
def login(username: str, password: str, response: Response):
    if username not in fake_users or fake_users[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(uuid.uuid4())
    # itsdangerous serializes the payload and appends a cryptographic signature
    signed_token = serializer.dumps({"user_id": user_id, "username": username})

    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=1800,
    )
    return {"message": "Login successful"}


@app.get("/profile")
def get_profile(session_token: Optional[str] = Cookie(default=None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    try:
        data = serializer.loads(session_token)
    except BadSignature:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    return {"user_id": data["user_id"], "username": data["username"]}
