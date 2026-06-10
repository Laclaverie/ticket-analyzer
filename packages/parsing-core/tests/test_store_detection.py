from decimal import Decimal
from parsing_core.parser import ReceiptLineParser
from parsing_core.stores import StoreType
from parsing_core.detector import StoreDetector

def test_store_detector():
    detector = StoreDetector()

    assert detector.detect(["COSTCO WHOLESALE", "123 MAIN ST"]) == StoreType.COSTCO
    assert detector.detect(["IGA VIVA", "STREET NAME"]) == StoreType.IGA
    assert detector.detect(["WALMART", "HELLO"]) == StoreType.UNKNOWN

def test_generic_fallback_in_store_mode():
    # If a line doesn't match a specific store pattern, fallback to generic
    parser = ReceiptLineParser(store_type=StoreType.COSTCO)
    parsed = parser.parse_line("Some Weird Line 5.00")
    assert parsed.normalized_name == "some weird line"
    assert parsed.line_total == Decimal("5.00")
