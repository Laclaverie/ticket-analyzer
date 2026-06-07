# ADR-001 - Monorepo and Modular Boundaries

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

The project is early stage, expected to evolve quickly, and currently small in team size.
Main delivery pressure is speed with clean architecture, not organizational scaling.

The system includes:
- Android app
- Backend API
- Worker processing pipeline
- Web/PC client
- Shared domain and analytics logic

## Decision

Adopt a single monorepo with strict module boundaries.

Top-level structure:
- `apps/` for deployable applications
- `packages/` for shared business capabilities
- `db/` for migrations and schema artifacts
- `infra/` for deployment and runtime operations
- `tests/` for cross-app functional and contract tests

Boundary rule:
- Apps can depend on packages.
- Apps cannot depend directly on other apps.
- Shared packages may not import app code.

## Needs Addressed

- Fast iteration with one change set across mobile, backend, and analytics.
- Single source of truth for contracts and domain logic.
- Lower overhead in CI, versioning, and release operations.

## Risks

1. Repository grows and becomes slower over time.
2. Boundary violations lead to tight coupling.
3. CI becomes noisy and expensive if all apps test on every change.

## Mitigations

1. Enforce ownership and dependency rules with linters/graph checks.
2. Use path-based CI to run only impacted test suites.
3. Keep shared packages small and domain-focused.

## Increment Plan

Increment 1:
- Create monorepo skeleton and dependency rules.
- Set up path-based CI triggers.

Increment 2:
- Introduce package versioning policy for split-readiness.
- Add boundary checks as required gate.

Increment 3:
- Evaluate split triggers (team ownership, release cadence conflicts, CI pain).

## Exit Criteria

- New modules are placed using the agreed structure.
- No app-to-app imports in CI checks.
- Shared logic reused without copy/paste across apps.
