import re
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from typing import Optional
from .models import ParsedLineItem

_WHITESPACE_PATTERN = re.compile(r"\s+")

class BaseStoreParser(ABC):
    """Base class for store-specific parsing logic."""

    @abstractmethod
    def parse_line(self, line: str) -> Optional[ParsedLineItem]:
        """Parse a single line. Returns None if line is not a line item."""
        pass

    def _to_decimal(self, value: str) -> Decimal:
        normalized = value.replace(",", ".")
        try:
            return Decimal(normalized)
        except InvalidOperation:
            return Decimal("0")

    def _normalize_name(self, value: str) -> str:
        cleaned = _WHITESPACE_PATTERN.sub(" ", value.strip().lower())
        return cleaned or "unknown item"

class CostcoParser(BaseStoreParser):
    """Specific parser for Costco receipts."""
    # Costco often has: 1234567 ITEM NAME 10.99 E
    # Or: 1234567 ITEM NAME 2 x 5.00 10.00 E
    _COSTCO_ITEM_PATTERN = re.compile(
        r"^(?P<sku>\d{4,10})\s+(?P<name>.+?)\s+(?P<price>\d+[.,]\d{2})\s*(?P<tax>[EPHF])?$",
        re.IGNORECASE
    )

    _COSTCO_MULTI_ITEM_PATTERN = re.compile(
        r"^(?P<sku>\d{4,10})\s+(?P<name>.+?)\s+(?P<qty>\d+)\s*[xX]\s*(?P<unit>\d+[.,]\d{2})\s+(?P<total>\d+[.,]\d{2})\s*(?P<tax>[EPHF])?$",
        re.IGNORECASE
    )

    def parse_line(self, line: str) -> Optional[ParsedLineItem]:
        # Try multi-item first
        match = self._COSTCO_MULTI_ITEM_PATTERN.search(line)
        if match:
            return ParsedLineItem(
                normalized_name=self._normalize_name(match.group("name")),
                quantity=self._to_decimal(match.group("qty")),
                unit_price=self._to_decimal(match.group("unit")),
                line_total=self._to_decimal(match.group("total")),
                confidence=0.95
            )

        match = self._COSTCO_ITEM_PATTERN.search(line)
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
