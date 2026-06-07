# ADR-004 - Hybrid Ingestion and Processing Pipeline

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

Receipt capture happens on Android and must work offline.
Accurate normalization/classification can require heavier backend processing.
Full image retention is desired for reprocessing and model improvement.

## Decision

Use a hybrid pipeline:
- On-device phase for immediate OCR preview and user feedback.
- Server-side phase for heavy parsing, normalization, classification, and enrichment.

Processing mode:
- API persists upload and creates async processing jobs.
- Worker executes idempotent pipelines with traceability.

## Needs Addressed

- Good mobile UX even without network.
- Better extraction quality through backend processing.
- Ability to improve historical data by reprocessing retained images.

## Risks

1. Mismatch between device preview and final server classification.
2. Processing backlog if worker throughput is low.
3. Privacy/security exposure from retained images.

## Mitigations

1. Show processing state and confidence transitions in UI.
2. Add retry/backoff and queue observability.
3. Enforce encrypted transport, storage path hardening, and access controls.

## Increment Plan

Increment 1:
- Implement upload + async job + final parsed result.
- Keep raw OCR and final normalized output linked.

Increment 2:
- Add rule-based classification tuning with manual correction loop.
- Add reprocessing endpoint for selected receipts.

Increment 3:
- Add optional model adapters (including LLM-assisted matching) behind strategy interfaces.

## Exit Criteria

- Offline capture and delayed sync works reliably.
- Every normalized item is traceable to source image and raw text.
- Reprocessing does not duplicate records or corrupt history.
