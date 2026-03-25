import time
import uuid
from typing import Optional

from fastapi import FastAPI, Response, Cookie, HTTPException
from itsdangerous import URLSafeSerializer, BadSignature

app = FastAPI()

SECRET_KEY = "super-secret-key-change-in-production"
serializer = URLSafeSerializer(SECRET_KEY)

SESSION_LIFETIME = 300    # 5 minutes — session expires after this
RENEWAL_MIN = 180         # 3 minutes — start auto-renewal window
RENEWAL_MAX = 300         # 5 minutes — end of auto-renewal window

fake_users = {
    "admin": "password123",
    "user1": "secret",
}


@app.post("/login")
def login(username: str, password: str, response: Response):
    if username not in fake_users or fake_users[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "user_id": str(uuid.uuid4()),
        "username": username,
        "ts": int(time.time()),
    }
    signed_token = serializer.dumps(payload)

    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=SESSION_LIFETIME,
    )
    return {"message": "Login successful"}


@app.get("/profile")
def get_profile(
    response: Response,
    session_token: Optional[str] = Cookie(default=None),
):
    if session_token is None:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    try:
        data = serializer.loads(session_token)
    except BadSignature:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})

    now = int(time.time())
    elapsed = now - data["ts"]

    if elapsed > SESSION_LIFETIME:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})

    # Auto-renew when 3–5 minutes have passed since last activity
    if RENEWAL_MIN <= elapsed <= RENEWAL_MAX:
        new_payload = {**data, "ts": now}
        new_token = serializer.dumps(new_payload)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=SESSION_LIFETIME,
        )

    return {"user_id": data["user_id"], "username": data["username"]}
