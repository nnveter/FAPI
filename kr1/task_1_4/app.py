from fastapi import FastAPI
from models import User

app = FastAPI()


@app.post("/user")
def create_user(user: User):
    return {"message": f"User {user.name} created", "user": user}
