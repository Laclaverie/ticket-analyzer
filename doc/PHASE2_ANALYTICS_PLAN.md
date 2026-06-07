# Phase 2 Analytics Package Plan

Status: Proposed then implemented in this branch
Date: 2026-06-07
Scope: analytics-core package + API analytics endpoints

## Goal

Expose consumption analytics so the frontend can render category breakdowns
and spending trends over time without doing any SQL itself.

## Target Queries

| Query | Description |
|-------|-------------|
| Spending by category | Sum of line_total grouped by category_id for a time window |
| Spending by month | Sum of line_total grouped by year+month for a time window |
| Top items | Most-purchased item names by frequency or spend |
| Receipt count by month | Number of receipts per calendar month |

## Architecture

### `analytics-core` package

- Pure SQLAlchemy queries, no FastAPI dependency.
- Single `AnalyticsRepository` class, all methods accept a `Session`.
- Returns simple dataclass value objects (`CategorySpend`, `MonthlySpend`, etc.).
- No business logic — aggregation only.

### Design patterns

| Pattern | Where | Why |
|---------|-------|-----|
| Repository | `AnalyticsRepository` | All SQL in one place, easy to unit-test with real SQLite |
| Value Object | Result dataclasses | Immutable, hashable, serializable |

### API endpoints (in `api-service`)

New router `routers/analytics.py`:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/spending/by-category` | Category spend totals, optional date filter |
| GET | `/analytics/spending/by-month` | Monthly spend totals, optional date filter |
| GET | `/analytics/top-items` | Top N item names by spend |
| GET | `/analytics/receipts/by-month` | Receipt count per month |

All endpoints accept optional `?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`.

### Schemas

New `schemas/analytics.py`:
- `CategorySpendResponse`
- `MonthlySpendResponse`
- `TopItemResponse`
- `MonthlyReceiptCountResponse`

## Testing Plan

### analytics-core unit tests (real in-memory SQLite, no mocks)

- `spending_by_category` returns correct sums.
- `spending_by_month` groups by year+month correctly.
- `top_items` returns items sorted by spend descending.
- `receipts_by_month` counts receipts correctly.
- Date filtering excludes rows outside window.
- Empty DB returns empty lists, not errors.

### API endpoint tests

- Each GET returns 200 with correct shape.
- Date filter query params are applied.
- Empty response when no data.

## Acceptance Criteria

- `analytics-core` is a workspace package imported by `api-service`.
- All four endpoints return correct, paginated-friendly JSON.
- Full test suite passes at 0 failures.
