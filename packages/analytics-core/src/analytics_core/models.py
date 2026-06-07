from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class CategorySpend:
    category_id: str
    total_spend: Decimal


@dataclass(frozen=True)
class MonthlySpend:
    year: int
    month: int
    total_spend: Decimal


@dataclass(frozen=True)
class TopItem:
    normalized_name: str
    total_spend: Decimal
    occurrence_count: int


@dataclass(frozen=True)
class MonthlyReceiptCount:
    year: int
    month: int
    receipt_count: int
