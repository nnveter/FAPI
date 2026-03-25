from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    name: str
    age: int
    email: Optional[str] = None
    is_subscribed: bool = False
