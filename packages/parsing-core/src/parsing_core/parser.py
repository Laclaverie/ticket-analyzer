import re
from decimal import Decimal, InvalidOperation

from parsing_core.models import ParsedLineItem

_QTY_X_UNIT_PATTERN = re.compile(r"(?P<qty>\d+(?:[.,]\d+)?)\s*[xX]\s*(?P<unit>\d+(?:[.,]\d{2,3}))")
_MONEY_PATTERN = re.compile(r"\d+(?:[.,]\d{2,3})")
_WHITESPACE_PATTERN = re.compile(r"\s+")


class ReceiptLineParser:
    """Rule-based parser for OCR receipt lines."""

    def parse_line(self, line: str) -> ParsedLineItem:
        cleaned = _WHITESPACE_PATTERN.sub(" ", line.strip())
        if not cleaned:
            return ParsedLineItem("unknown item", None, None, None, 0.1)

        quantity = None
        unit_price = None
        line_total = None
        work = cleaned

        qty_match = _QTY_X_UNIT_PATTERN.search(work)
        if qty_match:
            quantity = self._to_decimal(qty_match.group("qty"))
            unit_price = self._to_decimal(qty_match.group("unit"))
            work = (work[: qty_match.start()] + " " + work[qty_match.end() :]).strip()

        money_matches = list(_MONEY_PATTERN.finditer(work))
        if money_matches:
            line_total = self._to_decimal(money_matches[-1].group(0))
            work = (work[: money_matches[-1].start()] + " " + work[money_matches[-1].end() :]).strip()

        if quantity and unit_price and line_total is None:
            line_total = (quantity * unit_price).quantize(Decimal("0.01"))

        if quantity is None and unit_price is None and line_total is not None:
            quantity = Decimal("1")
            unit_price = line_total

        normalized_name = self._normalize_name(work)
        confidence = 0.8 if line_total is not None else 0.4

        return ParsedLineItem(
            normalized_name=normalized_name,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            confidence=confidence,
        )

    @staticmethod
    def _normalize_name(value: str) -> str:
        cleaned = _WHITESPACE_PATTERN.sub(" ", value.strip().lower())
        return cleaned or "unknown item"

    @staticmethod
    def _to_decimal(value: str) -> Decimal:
        normalized = value.replace(",", ".")
        try:
            return Decimal(normalized)
        except InvalidOperation:
            return Decimal("0")
