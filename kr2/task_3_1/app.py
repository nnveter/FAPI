from fastapi import FastAPI
from models import UserCreate

app = FastAPI()


@app.post("/create_user")
def create_user(user: UserCreate):
    return {
        "message": f"User {user.name} created successfully",
        "user": user.model_dump()
    }
