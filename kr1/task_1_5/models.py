from pydantic import BaseModel, field_validator
from typing import Optional


class UserWithAge(BaseModel):
    name: str
    age: int
    email: Optional[str] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Age cannot be negative")
        if v > 150:
            raise ValueError("Age seems unrealistic")
        return v
