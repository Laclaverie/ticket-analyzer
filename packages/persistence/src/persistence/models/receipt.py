from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.base import Base

if TYPE_CHECKING:
    from persistence.models.receipt_item import ReceiptItemRawORM
    from persistence.models.processing_job import ProcessingJobORM


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReceiptORM(Base):
    __tablename__ = "receipts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    store: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    images: Mapped[list[ReceiptImageORM]] = relationship(
        "ReceiptImageORM", back_populates="receipt", cascade="all, delete-orphan"
    )
    items_raw: Mapped[list[ReceiptItemRawORM]] = relationship(
        "ReceiptItemRawORM", back_populates="receipt", cascade="all, delete-orphan"
    )
    processing_jobs: Mapped[list[ProcessingJobORM]] = relationship(
        "ProcessingJobORM", back_populates="receipt", cascade="all, delete-orphan"
    )


class ReceiptImageORM(Base):
    __tablename__ = "receipt_images"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    receipt_id: Mapped[str] = mapped_column(String, ForeignKey("receipts.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    receipt: Mapped[ReceiptORM] = relationship("ReceiptORM", back_populates="images")
