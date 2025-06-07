from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


class URLCreate(BaseModel):
    target_url: HttpUrl = Field(..., example="https://example.com/very/long/path?with=arguments")


class URLInfo(BaseModel):
    link: str = Field(..., example="http://localhost:8000/shortkey")
    orig_link: HttpUrl = Field(..., example="https://example.com/very/long/path?with=arguments")
    secret_key: str = Field(..., example="shortkey_secretpart")


class URLDetails(BaseModel):
    link: str = Field(..., example="http://localhost:8000/shortkey")
    orig_link: HttpUrl = Field(..., example="https://example.com/very/long/path?with=arguments")
    is_active: bool
    expires_at: datetime


class URLStatsResponse(BaseModel):
    link: str = Field(..., example="http://localhost:8000/shortkey")
    orig_link: HttpUrl = Field(..., example="https://example.com/very/long/path?with=arguments")
    last_hour_clicks: int
    last_day_clicks: int