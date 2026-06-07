from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from analytics_core.models import (
    CategorySpend,
    MonthlyReceiptCount,
    MonthlySpend,
    TopItem,
)
from persistence.models.receipt import ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM


def _to_datetime_start(d: Optional[date]) -> Optional[datetime]:
    if d is None:
        return None
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)


def _to_datetime_end(d: Optional[date]) -> Optional[datetime]:
    if d is None:
        return None
    return datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)


class AnalyticsRepository:
    """
    All analytics queries in one place.
    Accepts a SQLAlchemy Session; never commits.

    Repository pattern: callers never construct SQL directly.
    Value object pattern: all results are frozen dataclasses.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def spending_by_category(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[CategorySpend]:
        q = (
            self._db.query(
                ReceiptItemNormalizedORM.category_id,
                func.sum(ReceiptItemNormalizedORM.line_total).label("total"),
            )
            .filter(ReceiptItemNormalizedORM.category_id.isnot(None))
            .filter(ReceiptItemNormalizedORM.line_total.isnot(None))
        )
        q = self._apply_item_date_filter(q, from_date, to_date)
        q = q.group_by(ReceiptItemNormalizedORM.category_id)

        return [
            CategorySpend(category_id=row.category_id, total_spend=Decimal(str(row.total)))
            for row in q.all()
            if row.category_id
        ]

    def spending_by_month(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[MonthlySpend]:
        q = (
            self._db.query(
                func.strftime("%Y", ReceiptItemRawORM.created_at).label("year"),
                func.strftime("%m", ReceiptItemRawORM.created_at).label("month"),
                func.sum(ReceiptItemNormalizedORM.line_total).label("total"),
            )
            .join(ReceiptItemRawORM, ReceiptItemNormalizedORM.receipt_item_raw_id == ReceiptItemRawORM.id)
            .filter(ReceiptItemNormalizedORM.line_total.isnot(None))
        )
        q = self._apply_item_date_filter(q, from_date, to_date)
        q = q.group_by("year", "month").order_by("year", "month")

        return [
            MonthlySpend(year=int(row.year), month=int(row.month), total_spend=Decimal(str(row.total)))
            for row in q.all()
        ]

    def top_items(
        self,
        limit: int = 10,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[TopItem]:
        q = (
            self._db.query(
                ReceiptItemNormalizedORM.normalized_name,
                func.sum(ReceiptItemNormalizedORM.line_total).label("total_spend"),
                func.count(ReceiptItemNormalizedORM.id).label("count"),
            )
            .filter(ReceiptItemNormalizedORM.line_total.isnot(None))
        )
        q = self._apply_item_date_filter(q, from_date, to_date)
        q = (
            q.group_by(ReceiptItemNormalizedORM.normalized_name)
            .order_by(func.sum(ReceiptItemNormalizedORM.line_total).desc())
            .limit(limit)
        )

        return [
            TopItem(
                normalized_name=row.normalized_name,
                total_spend=Decimal(str(row.total_spend)),
                occurrence_count=row.count,
            )
            for row in q.all()
        ]

    def receipts_by_month(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[MonthlyReceiptCount]:
        q = (
            self._db.query(
                func.strftime("%Y", ReceiptORM.created_at).label("year"),
                func.strftime("%m", ReceiptORM.created_at).label("month"),
                func.count(ReceiptORM.id).label("count"),
            )
        )
        start = _to_datetime_start(from_date)
        end = _to_datetime_end(to_date)
        if start:
            q = q.filter(ReceiptORM.created_at >= start)
        if end:
            q = q.filter(ReceiptORM.created_at <= end)
        q = q.group_by("year", "month").order_by("year", "month")

        return [
            MonthlyReceiptCount(year=int(row.year), month=int(row.month), receipt_count=row.count)
            for row in q.all()
        ]

    def _apply_item_date_filter(self, q, from_date: Optional[date], to_date: Optional[date]):
        start = _to_datetime_start(from_date)
        end = _to_datetime_end(to_date)
        if start:
            q = q.filter(ReceiptItemRawORM.created_at >= start)
        if end:
            q = q.filter(ReceiptItemRawORM.created_at <= end)
        return q
