from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.base import Base

if TYPE_CHECKING:
    from persistence.models.receipt import ReceiptORM
    from persistence.models.category import CategoryORM


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReceiptItemRawORM(Base):
    __tablename__ = "receipt_items_raw"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    receipt_id: Mapped[str] = mapped_column(String, ForeignKey("receipts.id"), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    receipt: Mapped[ReceiptORM] = relationship("ReceiptORM", back_populates="items_raw")
    normalized_items: Mapped[list[ReceiptItemNormalizedORM]] = relationship(
        "ReceiptItemNormalizedORM", back_populates="raw_item", cascade="all, delete-orphan"
    )


class ReceiptItemNormalizedORM(Base):
    __tablename__ = "receipt_items_normalized"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    receipt_item_raw_id: Mapped[str] = mapped_column(
        String, ForeignKey("receipt_items_raw.id"), nullable=False
    )
    normalized_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    line_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    category_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("categories.id"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    classification_origin: Mapped[str] = mapped_column(String, nullable=False, default="rule")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    raw_item: Mapped[ReceiptItemRawORM] = relationship(
        "ReceiptItemRawORM", back_populates="normalized_items"
    )
    category: Mapped[Optional[CategoryORM]] = relationship("CategoryORM")
