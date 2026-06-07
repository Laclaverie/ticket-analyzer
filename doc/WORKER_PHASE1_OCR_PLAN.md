# Worker Phase 1 OCR Slice Plan and Architecture

Status: Proposed then implemented in this branch
Date: 2026-06-07
Scope: Replace worker placeholder extraction with OCR-capable processor architecture

## Goal

Introduce an OCR-capable processing path without breaking current pipeline guarantees:
1. Keep the same poller lifecycle and transaction boundaries.
2. Add an OCR processor strategy that persists raw and normalized output rows.
3. Keep runtime safe when Tesseract is not installed via deterministic fallback.
4. Select processor through configuration.

## Current State

- Worker uses a stub processor strategy by default.
- Poller lifecycle already handles `pending -> in_progress -> completed/failed`.
- Output persistence is placeholder-only and filename-derived.

## Target Design

### Processor Strategy Layer

- Keep `BaseProcessor` unchanged as strategy interface.
- Keep `StubProcessor` for local deterministic testing.
- Add `OcrProcessor` for OCR-driven extraction.

Why: open/closed design with pluggable processors and no poller changes.

### OCR Adapter Layer

- Add OCR client abstraction with one method:
  - `extract_text(image_path: str) -> str`
- Add `AutoOcrClient` implementation:
  - Use local `tesseract` CLI if available.
  - Fallback to deterministic filename-derived text if unavailable or failed.

Why: allows real OCR usage in environments that have Tesseract while preserving development portability.

### Processor Selection

- Add worker config setting `processor_kind` with values:
  - `ocr`
  - `stub`
- Add processor factory to construct selected strategy.

Why: explicit runtime behavior and easy switching by environment.

## Data Flow (OCR path)

1. Poller picks pending jobs and marks in-progress.
2. `OcrProcessor` loads job and receipt image.
3. OCR client returns extracted text.
4. Processor rewrites extracted rows for the receipt:
   - `receipt_items_raw` line-by-line
   - `receipt_items_normalized` placeholder normalization per line
5. Poller marks completed, or failed with message on exception.

## Testing Plan

### Unit

- `OcrProcessor` writes raw and normalized rows from OCR text lines.
- `OcrProcessor` falls back to one synthetic line if OCR text is empty.
- Processor factory returns correct strategy for each config value.
- Invalid processor config raises clear error.

### Regression

- Existing worker poller tests remain green.
- Existing e2e upload -> worker completion remains green.

## Acceptance Criteria

- Worker can run with `processor_kind=ocr` without requiring extra Python deps.
- OCR processor persists output rows deterministically in tests.
- Full test suite passes.

## Deferred

- Rich parsing and price extraction from OCR text.
- Category classification integration with taxonomy package.
- Retry policy and dead-letter queue for repeated failures.
