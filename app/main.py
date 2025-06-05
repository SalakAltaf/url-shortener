from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.routers import shortener

from app.database import Base, engine          # ➊ import Base & engine
from app import models                         # ➋ make sure models are imported

Base.metadata.create_all(bind=engine)          # ➌ create tables if they don't exist


app = FastAPI(
    title="URL Shortener API",
    version="0.1.0",
    description="API for URL shortening service"
)
app.include_router(shortener.router)


@app.get("/")
def read_root():
    return {"Greetings": "Welcome to the URL Shortener Service"}


# ---------- global HTTPException handler ----------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return all HTTP errors in a uniform JSON structure."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# ---------- custom OpenAPI with security scheme ----------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="URL Shortener API",
        version="0.1.0",
        description="API for URL shortening service",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": shortener.API_KEY_NAME,
            "description": "API Key needed to access stats endpoint",
        }
    }
    # Secure only the stats path
    for path in openapi_schema["paths"]:
        if path.startswith("/stats/"):
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi





