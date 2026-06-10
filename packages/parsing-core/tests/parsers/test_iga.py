from decimal import Decimal
from parsing_core.parsers.iga import IgaParser

def test_iga_parsing():
    parser = IgaParser()

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
