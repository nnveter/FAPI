from datetime import datetime

from fastapi import FastAPI, Response
from models import CommonHeaders

app = FastAPI()


@app.get("/headers")
def get_headers(headers: CommonHeaders):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }


@app.get("/info")
def get_info(headers: CommonHeaders, response: Response):
    server_time = datetime.now().isoformat(timespec="seconds")
    response.headers["X-Server-Time"] = server_time

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }
