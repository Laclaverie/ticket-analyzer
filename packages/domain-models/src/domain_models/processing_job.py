from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain_models.enums import ProcessingStatus


@dataclass(frozen=True)
class ProcessingJob:
    id: str
    receipt_id: str
    status: ProcessingStatus
    error_message: Optional[str]
    retry_count: int
    max_attempts: int
    next_retry_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ProcessingJob id cannot be empty")
        if not self.receipt_id:
            raise ValueError("ProcessingJob receipt_id cannot be empty")
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.next_retry_at is not None and self.next_retry_at.tzinfo is None:
            raise ValueError("next_retry_at must be timezone-aware when provided")
