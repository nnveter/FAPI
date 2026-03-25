import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

MODE = os.getenv("MODE", "DEV")
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "secret")

# Disable all automatic doc routes; we expose them manually with auth
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

security = HTTPBasic()


def verify_docs_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        DOCS_USER.encode("utf-8"),
    )
    correct_pass = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        DOCS_PASSWORD.encode("utf-8"),
    )
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@app.get("/docs", include_in_schema=False)
def get_docs(credentials: HTTPBasicCredentials = Depends(verify_docs_auth)):
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not found")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/openapi.json", include_in_schema=False)
def get_openapi_schema(credentials: HTTPBasicCredentials = Depends(verify_docs_auth)):
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not found")
    return JSONResponse(
        get_openapi(title=app.title, version=app.version, routes=app.routes)
    )


@app.get("/health")
def health():
    return {"status": "ok", "mode": MODE}
