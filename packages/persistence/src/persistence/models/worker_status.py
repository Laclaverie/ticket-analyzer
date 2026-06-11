from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from persistence.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorkerStatusORM(Base):
    __tablename__ = "worker_status"

    worker_id: Mapped[str] = mapped_column(String, primary_key=True)
    processor_kind: Mapped[str] = mapped_column(String, nullable=False)
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="online")
