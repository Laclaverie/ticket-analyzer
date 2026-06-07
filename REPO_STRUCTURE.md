# Repository Structure

This file is a quick map of the monorepo and its responsibilities.

## Top Level

- apps/: Deployable applications.
- packages/: Shared business logic and contracts.
- db/: Schema migrations and seed data.
- infra/: Deployment, scripts, and monitoring.
- tests/: Cross-application functional and contract tests.
- doc/: Architecture and ADRs.

## Apps

- apps/mobile-android/: Android application (capture, offline sync, mobile analytics).
- apps/web-client/: Desktop browser client (analysis and export).
- apps/api-service/: Public HTTP API.
- apps/worker-service/: Asynchronous processing pipeline.

## Packages

- packages/domain-models/: Core entities and value objects.
- packages/api-contracts/: API contracts and schemas.
- packages/parsing-core/: Parsing and normalization logic.
- packages/analytics-core/: Aggregation and trend logic.
- packages/taxonomy-core/: Category taxonomy and mapping rules.
- packages/test-fixtures/: Shared datasets and fixtures for tests.

## Tests

- tests/e2e/: End-to-end tests.
- tests/contract/: API contract tests.
- tests/performance-smoke/: Basic performance and load smoke checks.
