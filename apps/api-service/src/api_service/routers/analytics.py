from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from analytics_core.repository import AnalyticsRepository
from api_service.dependencies import DbDep
from api_service.schemas.analytics import (
    CategorySpendResponse,
    MonthlyReceiptCountResponse,
    MonthlySpendResponse,
    TopItemResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/spending/by-category", response_model=list[CategorySpendResponse])
def spending_by_category(
    db: DbDep = None,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
) -> list[CategorySpendResponse]:
    repo = AnalyticsRepository(db)
    results = repo.spending_by_category(from_date=from_date, to_date=to_date)
    return [CategorySpendResponse(category_id=r.category_id, total_spend=r.total_spend) for r in results]


@router.get("/spending/by-month", response_model=list[MonthlySpendResponse])
def spending_by_month(
    db: DbDep = None,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
) -> list[MonthlySpendResponse]:
    repo = AnalyticsRepository(db)
    results = repo.spending_by_month(from_date=from_date, to_date=to_date)
    return [MonthlySpendResponse(year=r.year, month=r.month, total_spend=r.total_spend) for r in results]


@router.get("/top-items", response_model=list[TopItemResponse])
def top_items(
    db: DbDep = None,
    limit: int = Query(10, ge=1, le=100),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
) -> list[TopItemResponse]:
    repo = AnalyticsRepository(db)
    results = repo.top_items(limit=limit, from_date=from_date, to_date=to_date)
    return [
        TopItemResponse(
            normalized_name=r.normalized_name,
            total_spend=r.total_spend,
            occurrence_count=r.occurrence_count,
        )
        for r in results
    ]


@router.get("/receipts/by-month", response_model=list[MonthlyReceiptCountResponse])
def receipts_by_month(
    db: DbDep = None,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
) -> list[MonthlyReceiptCountResponse]:
    repo = AnalyticsRepository(db)
    results = repo.receipts_by_month(from_date=from_date, to_date=to_date)
    return [
        MonthlyReceiptCountResponse(year=r.year, month=r.month, receipt_count=r.receipt_count)
        for r in results
    ]
