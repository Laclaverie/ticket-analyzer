import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from persistence.base import Base
import persistence.models  # noqa: F401
from persistence.models.receipt import ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM
from analytics_core.repository import AnalyticsRepository


@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/analytics_test.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = factory()
    yield session
    session.close()
    engine.dispose()


def _add_item(db, receipt_id: str, name: str, line_total, category_id: str, line_number: int = 1):
    raw = ReceiptItemRawORM(
        receipt_id=receipt_id, raw_text=name, line_number=line_number
    )
    db.add(raw)
    db.flush()
    normalized = ReceiptItemNormalizedORM(
        receipt_item_raw_id=raw.id,
        normalized_name=name,
        line_total=Decimal(str(line_total)) if line_total is not None else None,
        category_id=category_id,
        confidence=0.8,
        classification_origin="rule",
    )
    db.add(normalized)
    db.flush()
    return normalized


def _add_receipt(db) -> ReceiptORM:
    receipt = ReceiptORM(currency="EUR")
    db.add(receipt)
    db.flush()
    return receipt


# --- spending_by_category ---

def test_spending_by_category_empty_db(db_session):
    repo = AnalyticsRepository(db_session)
    assert repo.spending_by_category() == []


def test_spending_by_category_sums_correctly(db_session):
    r = _add_receipt(db_session)
    _add_item(db_session, r.id, "milk", "2.99", "food-fresh-dairy", 1)
    _add_item(db_session, r.id, "cheese", "3.50", "food-fresh-dairy", 2)
    _add_item(db_session, r.id, "shampoo", "5.00", "non-food-hygiene", 3)
    db_session.commit()

    repo = AnalyticsRepository(db_session)
    results = {r.category_id: r.total_spend for r in repo.spending_by_category()}

    assert results["food-fresh-dairy"] == Decimal("6.49")
    assert results["non-food-hygiene"] == Decimal("5.00")


def test_spending_by_category_excludes_null_line_total(db_session):
    r = _add_receipt(db_session)
    _add_item(db_session, r.id, "unknown", None, "food", 1)
    db_session.commit()

    repo = AnalyticsRepository(db_session)
    assert repo.spending_by_category() == []


# --- spending_by_month ---

def test_spending_by_month_empty_db(db_session):
    repo = AnalyticsRepository(db_session)
    assert repo.spending_by_month() == []


def test_spending_by_month_groups_correctly(db_session):
    r = _add_receipt(db_session)
    _add_item(db_session, r.id, "milk", "2.99", "food", 1)
    _add_item(db_session, r.id, "bread", "1.50", "food", 2)
    db_session.commit()

    repo = AnalyticsRepository(db_session)
    results = repo.spending_by_month()

    assert len(results) == 1
    assert results[0].total_spend == Decimal("4.49")


# --- top_items ---

def test_top_items_empty_db(db_session):
    repo = AnalyticsRepository(db_session)
    assert repo.top_items() == []


def test_top_items_sorted_by_spend_desc(db_session):
    r = _add_receipt(db_session)
    _add_item(db_session, r.id, "milk", "2.99", "food", 1)
    _add_item(db_session, r.id, "steak", "12.00", "food", 2)
    _add_item(db_session, r.id, "bread", "1.50", "food", 3)
    db_session.commit()

    repo = AnalyticsRepository(db_session)
    results = repo.top_items()

    assert results[0].normalized_name == "steak"
    assert results[1].normalized_name == "milk"
    assert results[2].normalized_name == "bread"


def test_top_items_respects_limit(db_session):
    r = _add_receipt(db_session)
    for i in range(5):
        _add_item(db_session, r.id, f"item{i}", str(i + 1), "food", i + 1)
    db_session.commit()

    repo = AnalyticsRepository(db_session)
    assert len(repo.top_items(limit=3)) == 3


# --- receipts_by_month ---

def test_receipts_by_month_empty_db(db_session):
    repo = AnalyticsRepository(db_session)
    assert repo.receipts_by_month() == []


def test_receipts_by_month_counts_correctly(db_session):
    _add_receipt(db_session)
    _add_receipt(db_session)
    db_session.commit()

    repo = AnalyticsRepository(db_session)
    results = repo.receipts_by_month()

    assert len(results) == 1
    assert results[0].receipt_count == 2
