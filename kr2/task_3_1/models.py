from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_subscribed: bool = False

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Age must be positive")
        return v
