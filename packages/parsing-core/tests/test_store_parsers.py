from decimal import Decimal
from parsing_core.parser import ReceiptLineParser
from parsing_core.stores import StoreType
from parsing_core.detector import StoreDetector

def test_costco_parsing():
    parser = ReceiptLineParser(store_type=StoreType.COSTCO)

    # Standard item
    parsed = parser.parse_line("1234567 MILK 10.99 E")
    assert parsed.normalized_name == "milk"
    assert parsed.quantity == Decimal("1")
    assert parsed.unit_price == Decimal("10.99")
    assert parsed.line_total == Decimal("10.99")
    assert parsed.confidence > 0.8

    # Multi-item
    parsed = parser.parse_line("7654321 BANANA 2 x 1.50 3.00 E")
    assert parsed.normalized_name == "banana"
    assert parsed.quantity == Decimal("2")
    assert parsed.unit_price == Decimal("1.50")
    assert parsed.line_total == Decimal("3.00")

def test_iga_parsing():
    parser = ReceiptLineParser(store_type=StoreType.IGA)

    # Standard item
    parsed = parser.parse_line("POMMES 4.99 G")
    assert parsed.normalized_name == "pommes"
    assert parsed.quantity == Decimal("1")
    assert parsed.unit_price == Decimal("4.99")

    # Multi-item
    parsed = parser.parse_line("EAU 12 @ 0.50 6.00")
    assert parsed.normalized_name == "eau"
    assert parsed.quantity == Decimal("12")
    assert parsed.unit_price == Decimal("0.50")
    assert parsed.line_total == Decimal("6.00")

def test_store_detector():
    detector = StoreDetector()

    assert detector.detect(["COSTCO WHOLESALE", "123 MAIN ST"]) == StoreType.COSTCO
    assert detector.detect(["IGA VIVA", "STREET NAME"]) == StoreType.IGA
    assert detector.detect(["WALMART", "HELLO"]) == StoreType.UNKNOWN

def test_generic_fallback_in_store_mode():
    # If a line doesn't match Costco pattern but we are in Costco mode, fallback to generic
    parser = ReceiptLineParser(store_type=StoreType.COSTCO)
    parsed = parser.parse_line("Some Weird Line 5.00")
    assert parsed.normalized_name == "some weird line"
    assert parsed.line_total == Decimal("5.00")
