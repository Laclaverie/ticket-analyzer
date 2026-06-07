# ticket-analyzer

Consumption intelligence project focused on supermarket receipts.

The goal is to understand personal and household consumption patterns over time.

## Current Status

- Architecture baseline documented in [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md)
- ADR set available in [doc/ADR/README.md](doc/ADR/README.md)
- Monorepo scaffold initialized for incremental implementation

## Monorepo Layout

- apps/: deployable applications
- packages/: shared business modules
- db/: migrations and schema artifacts
- infra/: deployment and operations assets
- tests/: cross-application tests

See [REPO_STRUCTURE.md](REPO_STRUCTURE.md) for the full map.

## Planned Apps

- Android app for capture, offline sync, and mobile analytics
- Web client for desktop analysis and export
- API service for ingestion and analytics queries
- Worker service for asynchronous parsing and classification

## Quality Baseline

- Unit tests for public business behaviors
- Functional smoke tests on commits
- Full functional and contract tests on pull requests

Details are captured in ADR-005.

