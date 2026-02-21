from datetime import datetime, UTC
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item, PriceObservation, User
from .schemas import (
    ItemCreate,
    ItemRead,
    ObservationRead,
    ExtractionPreviewRequest,
    ExtractionPreviewResponse,
)
from .extractor import extract_price_by_css, ExtractionError

Base.metadata.create_all(bind=engine)


def _ensure_owner_column() -> None:
    inspector = inspect(engine)
    if "items" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("items")}
    if "owner_id" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE items ADD COLUMN owner_id INTEGER"))


_ensure_owner_column()

app = FastAPI(title="BellaBell API", version="0.2.0")
UI_DIRECTORY = Path(__file__).parent / "ui"
app.mount("/ui", StaticFiles(directory=UI_DIRECTORY), name="ui")


def get_current_user(
    db: Session = Depends(get_db),
    user_identifier: str | None = Header(default=None, alias="X-User-Id"),
) -> User:
    if user_identifier is None or not user_identifier.strip():
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")

    normalized_identifier = user_identifier.strip()
    existing_user = db.query(User).filter(User.external_id == normalized_identifier).first()
    if existing_user is not None:
        return existing_user

    created_user = User(external_id=normalized_identifier)
    db.add(created_user)
    db.commit()
    db.refresh(created_user)
    return created_user


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(UI_DIRECTORY / "index.html")


@app.post("/items", response_model=ItemRead)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = Item(**payload.model_dump(), owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/items", response_model=list[ItemRead])
def list_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Item)
        .filter(Item.owner_id == current_user.id)
        .order_by(Item.created_at.desc())
        .all()
    )


@app.get("/items/{item_id}/history", response_model=list[ObservationRead])
def item_history(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return (
        db.query(PriceObservation)
        .filter(PriceObservation.item_id == item_id)
        .order_by(PriceObservation.checked_at.desc())
        .all()
    )


@app.post("/items/{item_id}/check", response_model=ObservationRead)
def check_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        _, parsed_price = extract_price_by_css(item.url, item.css_selector)
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch page: {exc}") from exc

    observation = PriceObservation(item_id=item.id, price=parsed_price)
    item.last_price = parsed_price
    item.last_checked_at = datetime.now(UTC)

    db.add(observation)
    db.commit()
    db.refresh(observation)

    return observation


@app.post("/extract/preview", response_model=ExtractionPreviewResponse)
def preview_extraction(payload: ExtractionPreviewRequest):
    try:
        raw_text, parsed_price = extract_price_by_css(payload.url, payload.css_selector)
        return ExtractionPreviewResponse(raw_text=raw_text, parsed_price=parsed_price)
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch page: {exc}") from exc
