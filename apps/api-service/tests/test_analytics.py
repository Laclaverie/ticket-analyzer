import io

from persistence.models.receipt import ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM


def _seed_item(db_session, receipt_id: str, name: str, line_total: str, category_id: str, line_number: int = 1):
    raw = ReceiptItemRawORM(receipt_id=receipt_id, raw_text=name, line_number=line_number)
    db_session.add(raw)
    db_session.flush()
    db_session.add(ReceiptItemNormalizedORM(
        receipt_item_raw_id=raw.id,
        normalized_name=name,
        line_total=line_total,
        category_id=category_id,
        confidence=0.8,
        classification_origin="rule",
    ))
    db_session.flush()


def test_spending_by_category_empty(client):
    response = client.get("/analytics/spending/by-category")
    assert response.status_code == 200
    assert response.json() == []


def test_spending_by_category_returns_data(client, db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()
    _seed_item(db_session, receipt.id, "milk", "2.99", "food-fresh-dairy")
    db_session.commit()

    response = client.get("/analytics/spending/by-category")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category_id"] == "food-fresh-dairy"


def test_spending_by_month_empty(client):
    response = client.get("/analytics/spending/by-month")
    assert response.status_code == 200
    assert response.json() == []


def test_spending_by_month_returns_data(client, db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()
    _seed_item(db_session, receipt.id, "bread", "1.50", "food-fresh-bread")
    db_session.commit()

    response = client.get("/analytics/spending/by-month")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "year" in data[0]
    assert "month" in data[0]


def test_top_items_empty(client):
    response = client.get("/analytics/top-items")
    assert response.status_code == 200
    assert response.json() == []


def test_top_items_returns_data(client, db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()
    _seed_item(db_session, receipt.id, "steak", "12.00", "food-fresh-meat-fish")
    db_session.commit()

    response = client.get("/analytics/top-items")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["normalized_name"] == "steak"
    assert data[0]["occurrence_count"] == 1


def test_top_items_limit_param(client, db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()
    for i in range(5):
        _seed_item(db_session, receipt.id, f"item{i}", str(i + 1), "food", i + 1)
    db_session.commit()

    response = client.get("/analytics/top-items?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_receipts_by_month_empty(client):
    response = client.get("/analytics/receipts/by-month")
    assert response.status_code == 200
    assert response.json() == []


def test_receipts_by_month_returns_data(client):
    client.post(
        "/receipts/upload",
        files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    response = client.get("/analytics/receipts/by-month")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["receipt_count"] == 1
