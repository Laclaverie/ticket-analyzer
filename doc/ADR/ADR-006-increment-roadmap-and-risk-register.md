# ADR-006 - Increment Roadmap and Risk Register

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

The project is intentionally iterative and currently unconstrained by legacy systems.
A clear sequence is needed to balance delivery speed, quality, and architecture health.

## Decision

Adopt a 4-increment roadmap where each increment delivers user value and reduces structural risk.

## Needs Addressed

- Deliver useful analytics early.
- Keep architecture clean while moving quickly.
- De-risk future requirements (shared consumption contexts, auth, scaling).

## Increment Plan

### Increment 1 - Ingestion and Core Analytics (MVP)

Needs:
- Android receipt capture with offline storage/sync.
- Upload pipeline with async processing.
- Core consumption analytics on mobile and PC web.
- Export in machine-readable formats.

Main risks:
1. OCR quality variability by receipt format.
2. Parser quality instability across stores.
3. Slow feedback loops if pipeline observability is weak.

Mitigations:
1. Keep raw artifacts for iterative parser improvement.
2. Use rule-based normalization with explicit confidence scores.
3. Add processing status tracking and failure dashboards.

### Increment 2 - Consumption Contexts (Personal/Shared/For Others)

Needs:
- Data model support for consumption contexts.
- Context-aware analytics and filtering.
- Context assignment workflow per receipt/item.

Main risks:
1. Ambiguous context attribution by users.
2. Analytics confusion if context semantics are unclear.

Mitigations:
1. Provide explicit context definitions and defaults.
2. Preserve audit trail and allow reassignment.

### Increment 3 - Classification Intelligence Upgrade

Needs:
- Better category mapping and product identity resolution.
- Optional advanced model adapters (LLM or specialized classifier).
- Reprocessing tooling for historical data.

Main risks:
1. Non-deterministic model outputs.
2. Cost/performance spikes from advanced inference.

Mitigations:
1. Keep deterministic baseline classifier as fallback.
2. Wrap advanced models behind strategy interfaces and quotas.

### Increment 4 - Hardening and Scale Readiness

Needs:
- PostgreSQL readiness validation.
- Optional auth activation and multi-user isolation.
- Operational hardening (backup, monitoring, disaster recovery).

Main risks:
1. Migration regressions.
2. Security misconfiguration in self-hosted deployments.

Mitigations:
1. Run dual-engine compatibility tests before migration.
2. Provide deployment checklists and secure defaults.

## Global Risk Register (Cross-Increment)

1. Privacy risk from retained receipt images.
Mitigation: strict transport security, storage access control, and retention governance.

2. Domain drift from inconsistent taxonomy updates.
Mitigation: versioned taxonomy snapshots and change audit logs.

3. Architecture erosion under delivery pressure.
Mitigation: ADR updates, dependency boundary checks, and mandatory code review checklist.

4. Test debt accumulation.
Mitigation: enforce regression tests on bug fixes and protect CI gates.

## Exit Criteria

- Each increment has demonstrable user value.
- Risks are reviewed and updated at increment end.
- ADR set remains current with implementation reality.
