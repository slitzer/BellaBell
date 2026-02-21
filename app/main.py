from datetime import datetime, UTC

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item, PriceObservation
from .schemas import (
    ItemCreate,
    ItemRead,
    ObservationRead,
    ExtractionPreviewRequest,
    ExtractionPreviewResponse,
)
from .extractor import extract_price_by_css, ExtractionError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BellaBell API", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/items", response_model=ItemRead)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/items", response_model=list[ItemRead])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).order_by(Item.created_at.desc()).all()


@app.get("/items/{item_id}/history", response_model=list[ObservationRead])
def item_history(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return (
        db.query(PriceObservation)
        .filter(PriceObservation.item_id == item_id)
        .order_by(PriceObservation.checked_at.desc())
        .all()
    )


@app.post("/items/{item_id}/check", response_model=ObservationRead)
def check_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
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
