from fastapi import FastAPI
from models import UserWithAge

app = FastAPI()


@app.post("/user")
def create_user(user: UserWithAge):
    if user.age >= 18:
        return {"message": f"Welcome, {user.name}! You are an adult.", "user": user}
    return {"message": f"Sorry, {user.name}. You are underage.", "user": user}
