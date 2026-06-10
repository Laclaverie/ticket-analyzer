import re
from decimal import Decimal
from typing import Optional
from ..models import ParsedLineItem
from .base import BaseStoreParser

class IgaParser(BaseStoreParser):
    """Specific parser for IGA receipts."""
    # IGA often has: ITEM NAME 10.99 G
    # Or: ITEM NAME 2 @ 1.50 3.00
    _IGA_ITEM_PATTERN = re.compile(
        r"^(?P<name>.+?)\s+(?P<price>\d+[.,]\d{2})\s*(?P<tax>[GFT])?$",
        re.IGNORECASE
    )

    _IGA_MULTI_ITEM_PATTERN = re.compile(
        r"^(?P<name>.+?)\s+(?P<qty>\d+(?:[.,]\d+)?)\s*[@xX]\s*(?P<unit>\d+[.,]\d{2})\s+(?P<total>\d+[.,]\d{2})\s*(?P<tax>[GFT])?$",
        re.IGNORECASE
    )

    def parse_line(self, line: str) -> Optional[ParsedLineItem]:
        match = self._IGA_MULTI_ITEM_PATTERN.search(line)
        if match:
            return ParsedLineItem(
                normalized_name=self._normalize_name(match.group("name")),
                quantity=self._to_decimal(match.group("qty")),
                unit_price=self._to_decimal(match.group("unit")),
                line_total=self._to_decimal(match.group("total")),
                confidence=0.95
            )

        match = self._IGA_ITEM_PATTERN.search(line)
        if match:
            price = self._to_decimal(match.group("price"))
            return ParsedLineItem(
                normalized_name=self._normalize_name(match.group("name")),
                quantity=Decimal("1"),
                unit_price=price,
                line_total=price,
                confidence=0.9
            )

        return None
