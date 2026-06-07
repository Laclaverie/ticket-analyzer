# ADR-005 - Testing Strategy and Quality Gates

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

The project aims for clean delivery with strong reliability from the beginning.
The goal is not arbitrary coverage percentages, but confidence in behavior and regressions.

## Decision

Adopt a behavior-first test pyramid with mandatory CI gates.

Pyramid:
- Unit tests: dominant layer for public domain/core behaviors.
- Integration tests: API/DB, worker/DB, storage integrations.
- Functional tests: end-to-end critical flows.

Gate policy:
- Every commit: lint, typecheck, all unit tests, functional smoke subset.
- Every pull request: all commit checks + full functional suite + contract tests + migration tests.

## Needs Addressed

- Fast feedback on each commit.
- Strong confidence before merge.
- Regression prevention in ingestion and analytics workflows.

## Risks

1. Slow CI if suites are not partitioned.
2. Flaky functional tests reduce trust.
3. Under-tested edge cases despite many tests.

## Mitigations

1. Parallelize test execution and cache dependencies.
2. Stabilize e2e fixtures and isolate external dependencies.
3. Add regression tests for every bug fix and high-risk parser edge case.

## Increment Plan

Increment 1:
- Establish test harnesses and required CI checks.
- Cover all public domain functions with unit tests.

Increment 2:
- Add full ingestion e2e suite with offline-sync scenario.
- Add contract tests from OpenAPI.

Increment 3:
- Add performance smoke tests and long dataset scenarios.

## Exit Criteria

- No merge without passing quality gates.
- Bug fixes include regression tests.
- Functional suite consistently reliable and non-flaky.
