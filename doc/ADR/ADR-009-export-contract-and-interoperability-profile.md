# ADR-009 - Export Contract and Interoperability Profile

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

A core product requirement is that consumption data must be easily reusable by other tools.
Export must work reliably for analytics users and future automation workflows.

Early ambiguity exists around export formats and schema stability.

## Decision

Define an explicit export interoperability profile with two mandatory formats:
- CSV for tabular compatibility
- JSON for structured machine integration

Export contract principles:
- Stable field names and semantic meaning per version.
- UTF-8 encoding everywhere.
- ISO-8601 timestamps in UTC.
- Deterministic decimal serialization using dot separator.
- Explicit version metadata embedded in each export payload.

Supported export entities (Iteration 1 minimum):
- receipts
- receipt_items
- categories
- products (normalized catalog view)
- analytics snapshots (aggregated outputs)

## Needs Addressed

- Importability into spreadsheets, BI tools, and scripts.
- Predictable downstream processing with minimal manual cleanup.
- Backward-compatible export evolution.

## Risks

1. Schema drift breaks user automation scripts.
2. Locale-specific formatting causes parsing failures.
3. Large exports become slow or memory-heavy.

## Mitigations

1. Version export schemas and publish changelog.
2. Enforce locale-agnostic formatting rules.
3. Use streaming/chunked export for large datasets.

## Increment Plan

Increment 1:
- Deliver CSV and JSON exports for core entities.
- Add schema docs and sample files.

Increment 2:
- Add filtered and date-windowed exports.
- Add contract tests for format and schema validation.

Increment 3:
- Add signed export manifests and optional compression profiles.
- Add compatibility test matrix for common consumer tools.

## Revisit Triggers

- Frequent requests for Excel-native or parquet outputs.
- Integrations needing stricter schema guarantees.
- Export sizes that exceed acceptable generation time.

## Exit Criteria

- Exports are deterministic and versioned.
- Contract tests detect schema or format regressions.
- At least one sample import succeeds in spreadsheet and script-based workflows.
