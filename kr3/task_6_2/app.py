import secrets

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from models import User, UserInDB

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict[str, UserInDB] = {}


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    user = fake_users_db.get(credentials.username)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        user.username.encode("utf-8"),
    )
    correct_password = pwd_context.verify(credentials.password, user.hashed_password)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@app.post("/register", status_code=201)
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=hashed,
    )
    return {"message": f"User {user.username} registered successfully"}


@app.get("/login")
def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}
