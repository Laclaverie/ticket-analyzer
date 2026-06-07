from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from domain_models.enums import ClassificationOrigin


@dataclass(frozen=True)
class ReceiptItemRaw:
    id: str
    receipt_id: str
    raw_text: str
    line_number: int
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ReceiptItemRaw id cannot be empty")
        if not self.receipt_id:
            raise ValueError("ReceiptItemRaw receipt_id cannot be empty")
        if self.line_number < 0:
            raise ValueError("line_number must be non-negative")


@dataclass(frozen=True)
class ReceiptItemNormalized:
    id: str
    receipt_item_raw_id: str
    normalized_name: str
    quantity: Optional[Decimal]
    unit_price: Optional[Decimal]
    line_total: Optional[Decimal]
    category_id: Optional[str]
    confidence: float
    classification_origin: ClassificationOrigin
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ReceiptItemNormalized id cannot be empty")
        if not self.receipt_item_raw_id:
            raise ValueError("ReceiptItemNormalized receipt_item_raw_id cannot be empty")
        if not self.normalized_name:
            raise ValueError("normalized_name cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
