from decimal import Decimal
from parsing_core.parsers.costco import CostcoParser

def test_costco_parsing():
    parser = CostcoParser()

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
