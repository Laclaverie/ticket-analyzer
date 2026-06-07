# ADR-010 - Observability Baseline and SLOs

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

The system includes asynchronous processing, offline sync behavior, and multiple clients.
Without early observability, failures become hard to debug and quality degrades quickly.

As a side project, observability must be pragmatic and lightweight.

## Decision

Adopt a minimum viable observability stack from Iteration 1:
- Structured logs across all services.
- Core metrics for ingestion, processing, sync, and export.
- Correlation IDs propagated from client request through worker jobs.
- Lightweight health endpoints and readiness checks.

Define initial service-level objectives (SLOs):
- Ingestion acceptance reliability: 99.5% successful accepted uploads over 30-day window.
- Processing completion latency: 95% of receipts fully processed within 5 minutes.
- Export generation latency: 95% of standard exports completed within 20 seconds.

## Needs Addressed

- Fast incident triage with minimal tooling overhead.
- Visibility on OCR/parser quality and queue health.
- Baseline for reliability improvements over increments.

## Risks

1. Missing signals hide regressions in async pipeline.
2. Excessive logging increases storage and noise.
3. SLOs become aspirational only if not reviewed.

## Mitigations

1. Define required event points for each pipeline stage.
2. Use structured log levels and retention policies.
3. Review SLO dashboard at each increment end.

## Metric Baseline

Mandatory metrics:
- upload_requests_total
- upload_failures_total
- processing_jobs_total by status
- processing_latency_seconds
- queue_depth
- export_requests_total
- export_latency_seconds
- classification_confidence_distribution

Mandatory traces/events:
- request_id and job_id on all ingestion-processing steps.
- state transitions for each processing job.

## Increment Plan

Increment 1:
- Add structured logging and core metrics.
- Build simple dashboard for queue depth and failure counts.

Increment 2:
- Add end-to-end correlation from mobile sync event to analytics availability.
- Add alert rules for queue backlog and repeated processing failures.

Increment 3:
- Add quality metrics for taxonomy mapping drift and reprocessing outcomes.
- Tune SLO targets based on real usage data.

## Revisit Triggers

- Repeated incidents without clear root cause.
- Growth in async workload or client count.
- Migration to multi-user authentication model.

## Exit Criteria

- Core metrics are collected and visible.
- SLOs are measurable and reviewed periodically.
- Most ingestion/processing failures are diagnosable from logs and metrics alone.
