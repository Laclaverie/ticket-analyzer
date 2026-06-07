from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class UploadReceiptResponse(BaseModel):
    receipt_id: str
    job_id: str
    message: str = "Receipt uploaded and queued for processing."


class ReceiptImageResponse(BaseModel):
    id: str
    file_path: str
    file_hash: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReceiptResponse(BaseModel):
    id: str
    store: Optional[str]
    purchase_date: Optional[datetime]
    total_amount: Optional[Decimal]
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReceiptDetailResponse(ReceiptResponse):
    images: list[ReceiptImageResponse]


class ReceiptListResponse(BaseModel):
    items: list[ReceiptResponse]
    total: int
    page: int
    page_size: int
