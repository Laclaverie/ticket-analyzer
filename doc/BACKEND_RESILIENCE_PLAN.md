# Backend Resilience Plan

Status: Proposed then implemented in this branch
Date: 2026-06-07
Scope: retry/backoff for worker jobs and Docker runtime polish

## Goal

Finish the backend before frontend work by making the worker resilient and the local runtime reproducible.

## Why this slice

- The current worker marks failures as terminal immediately.
- Short-lived OCR/transient filesystem issues can recover on retry.
- Docker Compose already exists but does not expose all worker settings explicitly.

## Target Design

### 1) Retry metadata on processing jobs

Add to `processing_jobs`:
- `retry_count` integer, starts at `0`
- `max_attempts` integer, defaults to `3`
- `next_retry_at` datetime, nullable

Rules:
- `pending` jobs are eligible only when `next_retry_at` is null or in the past.
- On processor failure:
  - increment `retry_count`
  - if `retry_count < max_attempts`, set status back to `pending`
  - set `next_retry_at` using a fixed backoff delay
  - else mark `failed`

### 2) Worker poller behavior

- Keep `in_progress` transition before processor execution.
- Keep terminal `completed` on success.
- Add deterministic backoff delay calculation.
- Leave `failed` only for exhausted retries.

### 3) Docker Compose

- Make worker processor kind explicit in compose.
- Ensure API and worker both use the same SQLite volume and service settings.

## Functional tests to add

### Unit / integration

- Job repo creates retry metadata with defaults.
- Pending query ignores jobs waiting for retry.
- Poller failure on first attempt requeues job with retry metadata.
- Poller failure after max attempts marks job `failed`.
- Retry job becomes eligible after `next_retry_at` passes.

### Existing functional coverage to keep

- Upload -> queued job.
- Upload -> worker completes -> API read endpoints.
- Analytics endpoints.

## Acceptance criteria

- Backend can absorb transient worker failures without losing jobs.
- Docker Compose starts both services with explicit worker processor selection.
- Full test suite passes.
