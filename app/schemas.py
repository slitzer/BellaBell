from datetime import datetime
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    url: str
    css_selector: str = Field(min_length=1, max_length=200)
    check_interval_minutes: int = Field(default=60, ge=5, le=1440)


class ItemRead(BaseModel):
    id: int
    name: str
    url: str
    css_selector: str
    check_interval_minutes: int
    last_price: float | None
    last_checked_at: datetime | None

    model_config = {"from_attributes": True}


class ObservationRead(BaseModel):
    id: int
    item_id: int
    price: float
    checked_at: datetime

    model_config = {"from_attributes": True}


class ExtractionPreviewRequest(BaseModel):
    url: str
    css_selector: str


class ExtractionPreviewResponse(BaseModel):
    raw_text: str
    parsed_price: float
