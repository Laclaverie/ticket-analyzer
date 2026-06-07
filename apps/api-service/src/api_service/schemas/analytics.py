from decimal import Decimal

from pydantic import BaseModel


class CategorySpendResponse(BaseModel):
    category_id: str
    total_spend: Decimal


class MonthlySpendResponse(BaseModel):
    year: int
    month: int
    total_spend: Decimal


class TopItemResponse(BaseModel):
    normalized_name: str
    total_spend: Decimal
    occurrence_count: int


class MonthlyReceiptCountResponse(BaseModel):
    year: int
    month: int
    receipt_count: int
