from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class RawItemResponse(BaseModel):
    id: str
    receipt_id: str
    raw_text: str
    line_number: int
    created_at: datetime

    model_config = {"from_attributes": True}


class NormalizedItemResponse(BaseModel):
    id: str
    receipt_item_raw_id: str
    raw_text: Optional[str] = None
    normalized_name: str
    quantity: Optional[Decimal]
    unit_price: Optional[Decimal]
    line_total: Optional[Decimal]
    category_id: Optional[str]
    confidence: float
    classification_origin: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReceiptItemsResponse(BaseModel):
    receipt_id: str
    items: list[NormalizedItemResponse]
