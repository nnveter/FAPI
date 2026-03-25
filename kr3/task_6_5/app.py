import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db: dict[str, dict] = {}


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Authorization failed")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.post("/register", status_code=201)
@limiter.limit("1/minute")
def register(request: Request, body: RegisterRequest):
    if body.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed = pwd_context.hash(body.password)
    fake_users_db[body.username] = {
        "username": body.username,
        "hashed_password": hashed,
    }
    return {"message": "New user created"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest):
    user = fake_users_db.get(body.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    correct_username = secrets.compare_digest(
        body.username.encode("utf-8"),
        user["username"].encode("utf-8"),
    )
    if not correct_username or not pwd_context.verify(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Authorization failed")

    token = create_access_token({"sub": body.username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected_resource")
def protected(username: str = Depends(get_current_user)):
    return {"message": "Access granted"}
