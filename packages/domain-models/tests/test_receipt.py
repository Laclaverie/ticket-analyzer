import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal

from domain_models.receipt import Receipt, ReceiptImage


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_receipt(**kwargs) -> Receipt:
    defaults = dict(
        id="receipt-1",
        store="TestStore",
        purchase_date=None,
        total_amount=None,
        currency="EUR",
        created_at=_now(),
    )
    return Receipt(**{**defaults, **kwargs})


def test_receipt_creation_succeeds():
    receipt = _make_receipt()
    assert receipt.id == "receipt-1"
    assert receipt.currency == "EUR"


def test_receipt_is_immutable():
    receipt = _make_receipt()
    with pytest.raises(FrozenInstanceError):
        receipt.id = "other"  # type: ignore[misc]


def test_receipt_rejects_empty_id():
    with pytest.raises(ValueError, match="id"):
        _make_receipt(id="")


def test_receipt_rejects_empty_currency():
    with pytest.raises(ValueError, match="currency"):
        _make_receipt(currency="")


def test_receipt_rejects_currency_not_three_chars():
    with pytest.raises(ValueError, match="3-character"):
        _make_receipt(currency="EURO")


def test_receipt_accepts_two_char_currency_not_raising_length_rule():
    with pytest.raises(ValueError, match="3-character"):
        _make_receipt(currency="EU")


def test_receipt_accepts_optional_fields_as_none():
    receipt = _make_receipt(store=None, purchase_date=None, total_amount=None)
    assert receipt.store is None
    assert receipt.purchase_date is None
    assert receipt.total_amount is None


def test_receipt_stores_total_amount():
    receipt = _make_receipt(total_amount=Decimal("42.50"))
    assert receipt.total_amount == Decimal("42.50")


def test_receipt_image_creation_succeeds():
    img = ReceiptImage(
        id="img-1",
        receipt_id="receipt-1",
        file_path="/data/images/receipt-1/original.jpg",
        file_hash="abc123",
        created_at=_now(),
    )
    assert img.receipt_id == "receipt-1"
    assert img.file_hash == "abc123"


def test_receipt_image_is_immutable():
    img = ReceiptImage(
        id="img-1", receipt_id="r1", file_path="/p", file_hash="h", created_at=_now()
    )
    with pytest.raises(FrozenInstanceError):
        img.id = "other"  # type: ignore[misc]


def test_receipt_image_rejects_empty_file_path():
    with pytest.raises(ValueError, match="file_path"):
        ReceiptImage(id="i1", receipt_id="r1", file_path="", file_hash="h", created_at=_now())


def test_receipt_image_rejects_empty_file_hash():
    with pytest.raises(ValueError, match="file_hash"):
        ReceiptImage(id="i1", receipt_id="r1", file_path="/p", file_hash="", created_at=_now())
