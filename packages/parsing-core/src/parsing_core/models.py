from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class ParsedLineItem:
    normalized_name: str
    quantity: Optional[Decimal]
    unit_price: Optional[Decimal]
    line_total: Optional[Decimal]
    confidence: float
