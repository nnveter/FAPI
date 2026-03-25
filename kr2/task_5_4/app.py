from fastapi import FastAPI, Request, HTTPException

app = FastAPI()


@app.get("/headers")
def get_headers(request: Request):
    user_agent = request.headers.get("User-Agent")
    accept_language = request.headers.get("Accept-Language")

    if not user_agent:
        raise HTTPException(status_code=400, detail="User-Agent header is missing")
    if not accept_language:
        raise HTTPException(status_code=400, detail="Accept-Language header is missing")

    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language,
    }
