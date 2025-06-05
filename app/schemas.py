from pydantic import BaseModel, HttpUrl

class URLIn(BaseModel):
    url: HttpUrl

class URLOut(BaseModel):
    code: str
    short_url: HttpUrl

class URLStats(BaseModel):
    short_code: str
    clicks: int

class ErrorResponse(BaseModel):
    detail: str
