# Worker Phase 1 Execution Plan and Architecture

Status: Proposed then implemented in this branch
Date: 2026-06-07
Scope: Worker polling and job execution lifecycle for uploaded receipts

## Goal

Make the worker path production-shaped for Phase 1 while keeping implementation simple:
1. Pick pending jobs.
2. Transition status through `in_progress`.
3. Persist deterministic processing output for the receipt.
4. End in `completed` on success or `failed` with error details.

## Constraints

- Python 3.12+ workspace with uv.
- Single responsibility per module.
- Keep files small and easy to test.
- Poller owns transaction boundaries.
- Processor does domain work only; no commits.

## Current State

- API upload creates a pending job and stores image metadata.
- Worker poller processes pending jobs and marks directly as completed/failed.
- Stub processor is currently a no-op.

## Target Architecture

### 1) Poller Lifecycle (Template Method)

`JobPoller.poll_once` will orchestrate a strict lifecycle per job:
1. Mark job `in_progress` and commit.
2. Call processor strategy.
3. Mark `completed` and commit.
4. On error, rollback in-flight work, mark `failed` with message, commit.

Why: this makes job state observable and resilient in case of crashes.

### 2) Processor Strategy Responsibilities

`StubProcessor` remains a strategy implementation but now writes deterministic Phase 1 placeholder output:
- Read the job and its receipt image path.
- Replace previous extracted rows for the receipt (idempotent reruns).
- Insert one `receipt_items_raw` row and one linked `receipt_items_normalized` row.

Why: enables end-to-end flow validation before OCR and parsing adapters arrive.

### 3) Repository Contract

`JobRepository` remains worker-owned and gains `mark_in_progress`.

Why: status transitions stay centralized and testable.

## Data Flow

1. API uploads file and enqueues job (`pending`).
2. Worker polls and locks intent via `in_progress`.
3. Processor writes placeholder extraction output for the receipt.
4. Worker marks `completed`.
5. Failures mark job `failed` with `error_message`.

## Tests to Add/Update

### Unit Tests

- Poller marks `in_progress` before processing.
- Poller marks `failed` if processor raises.
- Stub processor inserts raw and normalized records.
- Stub processor is idempotent for reruns of same receipt/job context.

### Functional Slice

- Existing upload flow + one poll cycle leads to:
  - job status `completed`
  - at least one raw item and one normalized item in DB

## Acceptance Criteria

- Worker transitions statuses: `pending -> in_progress -> completed`.
- Worker transitions to `failed` and stores error message on processor exception.
- Processor persists deterministic output rows.
- Tests pass with `uv run pytest -q`.

## Deferred to Next Slice

- Real OCR adapter integration.
- Parser and taxonomy classifier integration.
- Retry/backoff and dead-letter strategy.
- Multi-worker concurrency controls.
