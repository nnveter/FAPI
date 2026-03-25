from pydantic import BaseModel, Field, field_validator

PROHIBITED_WORDS = ["кринж", "рофл", "вайб"]


class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("name", "message")
    @classmethod
    def no_prohibited_words(cls, v: str) -> str:
        lower = v.lower()
        for word in PROHIBITED_WORDS:
            if word in lower:
                raise ValueError(f"Prohibited word '{word}' found in the text")
        return v
