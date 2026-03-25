import secrets

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "secret123"


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        CORRECT_USERNAME.encode("utf-8"),
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        CORRECT_PASSWORD.encode("utf-8"),
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/login")
def login(username: str = Depends(verify_credentials)):
    return {"message": "You got my secret, welcome"}
