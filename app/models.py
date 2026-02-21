from datetime import datetime, UTC
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    css_selector: Mapped[str] = mapped_column(String(200), nullable=False)
    check_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    observations: Mapped[list["PriceObservation"]] = relationship(back_populates="item", cascade="all,delete")


class PriceObservation(Base):
    __tablename__ = "price_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

    item: Mapped[Item] = relationship(back_populates="observations")
