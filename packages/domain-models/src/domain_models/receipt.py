from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Receipt:
    id: str
    store: Optional[str]
    purchase_date: Optional[datetime]
    total_amount: Optional[Decimal]
    currency: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Receipt id cannot be empty")
        if not self.currency:
            raise ValueError("Receipt currency cannot be empty")
        if len(self.currency) != 3:
            raise ValueError("Currency must be a 3-character ISO code (e.g. EUR, CAD)")


@dataclass(frozen=True)
class ReceiptImage:
    id: str
    receipt_id: str
    file_path: str
    file_hash: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ReceiptImage id cannot be empty")
        if not self.receipt_id:
            raise ValueError("ReceiptImage receipt_id cannot be empty")
        if not self.file_path:
            raise ValueError("ReceiptImage file_path cannot be empty")
        if not self.file_hash:
            raise ValueError("ReceiptImage file_hash cannot be empty")
