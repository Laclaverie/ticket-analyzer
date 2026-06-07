# ADR-003 - Persistence Strategy: SQLite First, PostgreSQL Ready

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

The project starts as a self-hosted side project with limited operational overhead.
Storage must be simple now but capable of scaling and migration later.

## Decision

Primary database for early iterations: SQLite.

Migration intent:
- Prepare schema, repository layer, and tests for future PostgreSQL migration.

Storage split:
- Structured data in relational DB.
- Receipt images in filesystem object storage (path + hash in DB).

## Needs Addressed

- Fast setup and low maintenance.
- Easy backup and local portability.
- Clear progression path to stronger concurrency and scale.

## Risks

1. SQLite concurrency limitations with heavy parallel writes.
2. SQL portability issues if SQLite-specific features are used.
3. Long migration effort if repository boundaries are weak.

## Mitigations

1. Use job queues to smooth write bursts.
2. Avoid SQLite-only SQL extensions in core queries.
3. Keep persistence behind repositories and run dual-engine tests.

## Increment Plan

Increment 1:
- Build schema migrations and repositories for SQLite.
- Establish backup and restore scripts.

Increment 2:
- Add PostgreSQL compatibility tests in CI (non-blocking).
- Resolve non-portable SQL early.

Increment 3:
- Introduce PostgreSQL deployment profile and migration playbook.

## Exit Criteria

- All domain reads/writes go through repository interfaces.
- Migration scripts are versioned and repeatable.
- PostgreSQL compatibility status is visible in CI.
