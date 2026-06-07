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
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ProcessingJob id cannot be empty")
        if not self.receipt_id:
            raise ValueError("ProcessingJob receipt_id cannot be empty")
