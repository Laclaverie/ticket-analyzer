import re
from decimal import Decimal
from typing import Optional
from ..models import ParsedLineItem
from .base import BaseStoreParser

class CostcoParser(BaseStoreParser):
    """Specific parser for Costco receipts."""

    # Standard item: SKU NAME PRICE [TAX]
    # Price can have a '-' suffix for discounts (e.g., 2.00-)
    _COSTCO_ITEM_PATTERN = re.compile(
        r"^(?P<sku>\d{4,10})\s+(?P<name>.+?)\s+(?P<price>\d+[.,]\d{2})(?P<minus>-)?\s*(?P<tax>[EPHF])?$",
        re.IGNORECASE
    )

    # Multi-item: SKU NAME QTY x UNIT TOTAL [TAX]
    _COSTCO_MULTI_ITEM_PATTERN = re.compile(
        r"^(?P<sku>\d{4,10})\s+(?P<name>.+?)\s+(?P<qty>\d+(?:[.,]\d+)?)\s*[xX]\s*(?P<unit>\d+[.,]\d{2})\s+(?P<total>\d+[.,]\d{2})(?P<minus>-)?\s*(?P<tax>[EPHF])?$",
        re.IGNORECASE
    )

    def parse_line(self, line: str) -> Optional[ParsedLineItem]:
        # Try multi-item first
        match = self._COSTCO_MULTI_ITEM_PATTERN.search(line)
        if match:
            total = self._to_decimal(match.group("total"))
            if match.group("minus"):
                total = -total

            unit = self._to_decimal(match.group("unit"))
            qty = self._to_decimal(match.group("qty"))

            return ParsedLineItem(
                normalized_name=self._normalize_name(match.group("name")),
                quantity=qty,
                unit_price=unit,
                line_total=total,
                confidence=0.95
            )

        match = self._COSTCO_ITEM_PATTERN.search(line)
        if match:
            price = self._to_decimal(match.group("price"))
            if match.group("minus"):
                price = -price

            return ParsedLineItem(
                normalized_name=self._normalize_name(match.group("name")),
                quantity=Decimal("1"),
                unit_price=price,
                line_total=price,
                confidence=0.9
            )

        return None
