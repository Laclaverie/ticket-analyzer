# Worker Phase 1 Parsing Slice Plan and Architecture

Status: Proposed then implemented in this branch
Date: 2026-06-07
Scope: Parse OCR lines into structured item fields in a dedicated package

## Goal

Turn OCR text lines into structured item records while keeping responsibilities separated:
1. OCR layer extracts text only.
2. Parsing layer converts lines into structured fields.
3. Worker processor persists parsed output without owning parsing rules.

## Why This Slice

The current OCR path stores line text but still treats normalized fields as placeholders.
This slice introduces deterministic parsing for name, quantity, unit price, and line total.

## Target Architecture

### 1) New `parsing-core` Package

- Add `ParsedLineItem` value object.
- Add `ReceiptLineParser` service with rule-based parsing.
- Keep package independent of SQLAlchemy and worker internals.

### 2) Worker Integration (Dependency Injection)

- `OcrProcessor` receives a parser dependency.
- For each OCR line:
  - persist raw line
  - persist parsed normalized fields

Why: keeps processor orchestration-focused and open to future parser replacement.

### 3) Rule Set (Initial)

Support common receipt patterns:
- `NAME PRICE` (e.g., `Milk 2.99`)
- `NAME QTY x UNIT [TOTAL]` (e.g., `Tomato 2 x 1.49 2.98`)
- Empty/invalid lines fallback to normalized text only.

## Data Flow

1. OCR client returns text.
2. OCR processor splits non-empty lines.
3. Parser converts each line into `ParsedLineItem`.
4. Worker stores:
   - `receipt_items_raw.raw_text`
   - `receipt_items_normalized.normalized_name, quantity, unit_price, line_total`

## Testing Plan

### Unit: `parsing-core`

- Parse single price line.
- Parse qty x unit with explicit total.
- Parse qty x unit without total (derive total).
- Parse non-price line fallback.

### Integration: `worker-service`

- `OcrProcessor` persists parsed fields from OCR text lines.
- Existing worker and e2e tests remain green.

## Acceptance Criteria

- `parsing-core` exists as a workspace package and is imported by worker.
- `OcrProcessor` uses parser dependency rather than inline string lowering.
- Parsed numeric fields are persisted when extractable.
- Full test suite passes.

## Deferred

- Advanced locale/currency handling beyond basic decimal parsing.
- Multi-line item continuation handling.
- Taxonomy classification from parsed names.
