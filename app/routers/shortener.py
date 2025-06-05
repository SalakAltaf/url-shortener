import logging
import os
import random
import string

from fastapi import APIRouter, Depends, HTTPException, Security, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import URLIn, URLOut, URLStats, ErrorResponse  # <- use central Pydantic models

router = APIRouter()

# ---------- logging ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.routers.shortener")

# ---------- security ----------
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY is not set. Please define it in the environment.")

API_KEY_NAME = "token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header


# ---------- helper ----------
def generate_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


# ---------- endpoints ----------
@router.post(
    "/shorten",
    response_model=URLOut,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def shorten_url(url_in: URLIn, request: Request, db: Session = Depends(get_db)):
    """Create a short URL.  
    - Returns existing short URL with 201 if already shortened."""
    
    existing = (
        db.query(models.URL)
        .filter(models.URL.target_url == str(url_in.url))
        .first()
    )
    if existing:
        # Return existing short URL with 201 status (idempotent behavior)
        return {"code": existing.short_code, "short_url": f"{request.base_url}{existing.short_code}"}

    # Generate a unique short code
    code = generate_code()
    while db.query(models.URL).filter(models.URL.short_code == code).first():
        code = generate_code()

    new = models.URL(target_url=str(url_in.url), short_code=code)
    db.add(new)
    db.commit()
    db.refresh(new)

    return {"code": new.short_code, "short_url": f"{request.base_url}{new.short_code}"}


@router.get("/{short_code}", response_class=RedirectResponse, responses={404: {"model": ErrorResponse}})
def redirect_url(short_code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    item = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Increment click counter
    item.clicks += 1
    db.commit()

    logger.info(
        "Redirect requested: short_code=%s, target_url=%s, clicks=%d",
        short_code,
        item.target_url,
        item.clicks,
    )

    return RedirectResponse(url=item.target_url, status_code=307)


@router.get(
    "/stats/{short_code}",
    response_model=URLStats,
    responses={404: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def get_stats(
    short_code: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    """Return total click count for a short URL."""
    item = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return {"short_code": item.short_code, "clicks": item.clicks}







