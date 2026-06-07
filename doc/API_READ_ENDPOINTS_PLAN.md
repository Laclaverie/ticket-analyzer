# API Read Endpoints Plan

Status: Proposed then implemented in this branch
Date: 2026-06-07
Scope: Expose receipt, item, and job query endpoints to close Phase 1

## Goal

Allow any HTTP client to query the results of the ingestion pipeline:
- List receipts with pagination
- Get a single receipt with its images
- Get processed items for a receipt (raw lines + normalized fields + category)
- Get job status

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/receipts` | Paginated receipt list |
| GET | `/receipts/{receipt_id}` | Single receipt with images |
| GET | `/receipts/{receipt_id}/items` | Normalized items for a receipt |
| GET | `/jobs/{job_id}` | Job status and error |

## Design

### Schemas (Pydantic response models)

New file `schemas/items.py`:
- `RawItemResponse` — id, receipt_id, raw_text, line_number
- `NormalizedItemResponse` — id, normalized_name, quantity, unit_price, line_total, category_id, confidence, classification_origin
- `ReceiptItemsResponse` — receipt_id, items list

New schemas in `schemas/receipt.py`:
- `ReceiptResponse` — id, store, purchase_date, total_amount, currency, created_at
- `ReceiptListResponse` — items list, total count, page, page_size
- `ReceiptDetailResponse` — receipt + image list

New file `schemas/jobs.py`:
- `JobStatusResponse` — id, receipt_id, status, error_message, created_at, updated_at

### Repositories (new read queries)

`ReceiptRepository` gains:
- `list_all(offset, limit)` — paginated receipt list with total count
- `find_items(receipt_id)` — raw + normalized items joined

`JobRepository` gains nothing new — `find_by_id` already exists.

### Routers

`routers/receipts.py` gains GET routes.
New `routers/jobs.py` for job status.

### Patterns

- Repository pattern: all SQL stays in repository layer.
- No business logic in routers — routers translate HTTP ↔ repository.
- 404 via HTTPException when resource not found.

## Testing

- GET /receipts returns empty list when no data.
- GET /receipts returns receipts after upload.
- GET /receipts/{id} returns receipt detail.
- GET /receipts/{id} returns 404 for unknown id.
- GET /receipts/{id}/items returns items after worker processing.
- GET /jobs/{id} returns job status.
- GET /jobs/{id} returns 404 for unknown id.

## Acceptance Criteria

- All endpoints return correct shapes validated by Pydantic.
- 404s are raised for missing resources.
- Full test suite passes.
