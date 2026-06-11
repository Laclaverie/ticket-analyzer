import re
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from typing import Optional
from ..models import ParsedLineItem

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
