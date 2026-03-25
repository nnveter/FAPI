from pydantic import BaseModel
from fastapi import Header
from typing import Annotated


class CommonHeaders(BaseModel):
    user_agent: Annotated[str, Header(alias="user-agent")]
    accept_language: Annotated[str, Header(alias="accept-language")]

    model_config = {"populate_by_name": True}
