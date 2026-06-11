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

def test_costco_discounts_and_tricky_lines():
    parser = CostcoParser()

    # Negative price (discount)
    parsed = parser.parse_line("1955464 TPD/395960 6.00-")
    assert parsed.normalized_name == "tpd/395960"
    assert parsed.line_total == Decimal("-6.00")

    # Items with multiplier-like names but no 'x'
    parsed = parser.parse_line("1836474 SALAMI 3X300 16.99")
    assert parsed.normalized_name == "salami 3x300"
    assert parsed.quantity == Decimal("1")
    assert parsed.line_total == Decimal("16.99")

    # Item with explicit 'X' multiplier
    parsed = parser.parse_line("330328 EGGS 2 X 12 7.49")
    # Note: Currently the regex for multi-item expects SKU NAME QTY x UNIT TOTAL.
    # Lines like "EGGS 2 X 12 7.49" might be tricky if "12" is seen as price.
    # In the image, it looks like "330328 EGGS 2 X 12 7.49" -> SKU NAME QTY X UNIT PRICE.
    # Wait, in the image it says "330328 EGGS 2 X 12 7.49". 7.49 is the total.
    assert parsed.normalized_name == "eggs 2 x 12"
    assert parsed.line_total == Decimal("7.49")

def test_costco_from_image_sample():
    parser = CostcoParser()

    sample_lines = [
        "580517 **KS TOWEL** 24.99 H",
        "1130150 HUGG WIPE 30.99 H",
        "1947228 TPD/1130150 7.50- H",
        "330328 EGGS 2 X 12 7.49",
        "308937 SALMON 1.08 36.99", # Weight based? 1.08 is weight, 36.99 is price
    ]

    parsed = parser.parse_line(sample_lines[0])
    assert parsed.normalized_name == "**ks towel**"
    assert parsed.line_total == Decimal("24.99")

    parsed = parser.parse_line(sample_lines[2])
    assert parsed.normalized_name == "tpd/1130150"
    assert parsed.line_total == Decimal("-7.50")
