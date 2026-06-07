# Architecture Decision Records

This directory contains the decision log for Ticket Analyzer.

Conventions:
- ADRs are immutable once accepted. If a decision changes, add a new ADR that supersedes the old one.
- File naming: `ADR-XXX-short-title.md`.
- Status values: `Proposed`, `Accepted`, `Deprecated`, `Superseded`.
- Every ADR must include:
  - Context
  - Decision
  - Needs
  - Risks and mitigations
  - Increment plan

Current ADR set:
- ADR-001: Monorepo and modular boundaries
- ADR-002: API style and contract governance
- ADR-003: Persistence strategy (SQLite first)
- ADR-004: Hybrid ingestion and processing pipeline
- ADR-005: Testing strategy and quality gates
- ADR-006: Increment roadmap and risk register
- ADR-007: PC client delivery mode
- ADR-008: Security and authentication rollout
- ADR-009: Export contract and interoperability profile
- ADR-010: Observability baseline and SLOs
- ADR-011: Data governance and retention evolution policy
- ADR-012: Classification quality evaluation framework

Planned next ADR topics:
- API idempotency and conflict resolution policy
- Mobile offline sync conflict strategy
