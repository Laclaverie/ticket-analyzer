# ADR-011 - Data Governance and Retention Evolution Policy

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

The project currently keeps full receipt image retention to improve parsing and future features.
As data volume grows, governance and lifecycle policies are needed to preserve utility, privacy, and storage health.

The deployment model is self-hosted first, with region preference in Europe or Canada.

## Decision

Adopt a staged governance model with explicit retention classes and lifecycle actions.

Data classes:
- Class A: Raw receipt images and raw OCR text.
- Class B: Normalized transactional data (items, categories, prices, contexts).
- Class C: Derived analytics outputs and aggregates.
- Class D: Operational telemetry and audit logs.

Retention policy baseline:
- Class A: retained by default in Iteration 1, with optional manual purge controls.
- Class B: retained indefinitely (core longitudinal dataset).
- Class C: rebuildable from Class B, retention configurable.
- Class D: time-bounded retention with rotation.

Governance rules:
- Every record stores provenance metadata (source, parser version, processing timestamp).
- Reprocessing is append-and-reconcile, not destructive overwrite.
- Deletion actions are auditable.

## Needs Addressed

- Preserve historical learning value from receipts.
- Keep analytical continuity over years.
- Prepare for future privacy and multi-user governance requirements.

## Risks

1. Unbounded storage growth from raw images.
2. Inconsistent historical analytics after taxonomy or parser changes.
3. Governance drift when policies are implicit.

## Mitigations

1. Add storage dashboards and retention review checkpoints.
2. Version parser, taxonomy, and model metadata per processed record.
3. Keep governance policy as explicit ADR-backed operational runbook.

## Increment Plan

Increment 1:
- Persist provenance metadata and parser/taxonomy versions.
- Add manual purge/export commands for Class A data.

Increment 2:
- Add configurable retention profiles (for example: strict, balanced, archival).
- Add archive and restore workflow for raw images.

Increment 3:
- Add policy-driven automated lifecycle jobs with dry-run mode.
- Add retention compliance checks to operational dashboard.

## Revisit Triggers

- Storage cost or capacity pressure.
- New regulatory or household sharing requirements.
- Frequent reprocessing needs conflicting with retention settings.

## Exit Criteria

- Data classes and lifecycle actions are documented and enforced.
- Provenance is available for all normalized records.
- Retention actions are traceable and recoverable where intended.
