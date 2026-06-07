from decimal import Decimal

from parsing_core.parser import ReceiptLineParser


def test_parse_line_name_and_price():
    parser = ReceiptLineParser()
    parsed = parser.parse_line("Milk 2.99")

    assert parsed.normalized_name == "milk"
    assert parsed.quantity == Decimal("1")
    assert parsed.unit_price == Decimal("2.99")
    assert parsed.line_total == Decimal("2.99")


def test_parse_line_qty_x_unit_with_total():
    parser = ReceiptLineParser()
    parsed = parser.parse_line("Tomato 2 x 1.49 2.98")

    assert parsed.normalized_name == "tomato"
    assert parsed.quantity == Decimal("2")
    assert parsed.unit_price == Decimal("1.49")
    assert parsed.line_total == Decimal("2.98")


def test_parse_line_qty_x_unit_without_total_derives_total():
    parser = ReceiptLineParser()
    parsed = parser.parse_line("Banana 2 x 1.50")

    assert parsed.normalized_name == "banana"
    assert parsed.quantity == Decimal("2")
    assert parsed.unit_price == Decimal("1.50")
    assert parsed.line_total == Decimal("3.00")


def test_parse_line_without_price_uses_name_fallback():
    parser = ReceiptLineParser()
    parsed = parser.parse_line("Costco receipt")

    assert parsed.normalized_name == "costco receipt"
    assert parsed.quantity is None
    assert parsed.unit_price is None
    assert parsed.line_total is None
