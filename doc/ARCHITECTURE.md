# Ticket Analyzer - Architecture Foundation

Status: Draft v1 (design baseline)
Date: 2026-06-07
Scope: Foundation for Iteration 1 and Iteration 2

## 1. Product Intent

The product is a consumption intelligence app focused on supermarket receipts.

Primary objective:
- Understand personal and household consumption habits over time.

Out of scope for now:
- Budgeting workflows, financial planning, and budget alerts.

## 2. Confirmed Product Scope

### Iteration 1
- Receipt ingestion from Android phone.
- Offline-first capture on phone and later synchronization.
- OCR + parsing pipeline (hybrid: on-device and server-side).
- Analytics centered on consumption behavior.
- Single user (no authentication required for MVP).
- Full retention of receipt images on server/PC.

### Iteration 2
- Consumption contexts:
	- Personal (only me).
	- Shared with one or more people.
	- For other people.
- Context-aware analytics (example: products usually bought alone vs with others vs for groups).
- Multi-person semantics and optional authentication.

## 3. Architectural Principles

- Local control first: self-hosted deployment as the primary model.
- Secure by default: encrypted communication even in home/self-hosted usage.
- Offline-first mobile: capture must not depend on immediate connectivity.
- Explicit domain boundaries: ingestion, parsing, cataloging, analytics, and presentation are separated.
- Replaceable integrations: OCR/LLM providers are adapters, not core logic.
- Testability first: every public behavior in core modules must be testable in isolation.
- Migration-ready persistence: start with SQLite, keep compatibility for PostgreSQL migration.

## 4. Technology Choices

## 4.1 Summary

- Mobile app: Kotlin + Jetpack Compose (Android first).
- Backend API: Python FastAPI.
- Processing workers: Python (same codebase, separate runtime process).
- Data store (initial): SQLite.
- Object/file storage: local filesystem on server/PC, content-addressed layout.
- Queue for async jobs (initial): database-backed job table.
- API protocol: REST/JSON over HTTPS.
- Contract format: OpenAPI + JSON Schema for shared DTO contracts.
- PC access (Iteration 1): Browser web app.
- Desktop option (later): Tauri shell around web app if desktop packaging becomes preferred.

## 4.2 Why These Choices

### Kotlin + Compose for Android
- Best native support for camera integration, offline storage, and background sync.
- Strong long-term maintainability for Android-first delivery.

### FastAPI for API and services
- Fast implementation speed, typed APIs, and easy OpenAPI generation.
- Fits hybrid pipeline integration (OCR, parser, optional LLM connectors).

### SQLite first
- Simple operations for side project scale.
- Easy local backup and portability.
- Can be migrated later through controlled schema and repository boundaries.

### REST + OpenAPI contracts
- Simple interoperability across mobile, web, desktop wrapper, and processing workers.
- Contract tests can validate clients and server without coupling implementation details.

### Web app first for PC access
- Lowest friction to ship and iterate.
- Can still satisfy desktop preference later by wrapping the same web app with Tauri.

## 5. High-Level System Design

Core components:
- Android Client App
- API Service
- Processing Worker
- Analytics Query Layer
- SQLite Database
- Receipt Image Storage
- PC Web Client

Flow overview:
1. User captures receipt on phone.
2. Phone stores draft receipt locally (offline-safe).
3. On-device OCR runs for quick preview and immediate correction.
4. When online, phone uploads image + metadata + preliminary OCR result.
5. API persists raw data and enqueues processing job.
6. Worker runs normalization, line-item parsing, categorization, and confidence scoring.
7. Analytics layer exposes consumption-focused read endpoints.
8. Phone and PC clients visualize trends and allow export.

## 6. Monorepo Structure

A single monorepo is the default.

Proposed layout:

apps/
- mobile-android/
- web-client/
- api-service/
- worker-service/

packages/
- domain-models/
- api-contracts/
- parsing-core/
- analytics-core/
- taxonomy-core/
- test-fixtures/

infra/
- docker/
- reverse-proxy/
- scripts/
- monitoring/

db/
- migrations/
- seeds/
- schema-docs/

docs/
- architecture/
- adr/

tests/
- e2e/
- contract/
- performance-smoke/

## 6.1 Module Responsibilities

### apps/mobile-android
- Capture receipts, local draft persistence, offline sync.
- Quick on-device OCR preview.
- Consumption analytics visualization for mobile.
- No heavy normalization logic (delegated to backend).

### apps/web-client
- PC-facing analysis dashboard.
- Advanced filtering and export workflow.
- No business calculation duplicated from backend.

### apps/api-service
- Public API, validation, and orchestration.
- Receipt ingestion endpoints.
- Query endpoints for analytics and exports.
- Job scheduling for heavy processing.

### apps/worker-service
- Asynchronous processing pipeline.
- Parsing, normalization, categorization, confidence scoring.
- Optional LLM-assisted matching through adapter interface.

### packages/domain-models
- Canonical entities and value objects.
- Domain invariants and semantics.

### packages/api-contracts
- API DTO schemas and versioned contract definitions.
- Generated client stubs if needed.

### packages/parsing-core
- Parsing strategies, normalization rules, parser interfaces.

### packages/analytics-core
- Consumption metrics and aggregation logic.

### packages/taxonomy-core
- Category hierarchy, mapping rules, and editable taxonomy logic.

## 7. Shared Code vs Non-Shared Code

Share:
- Domain entities and enums.
- API schemas and validation contracts.
- Parsing/normalization core logic.
- Taxonomy definitions and categorization rules.
- Analytics aggregation logic.
- Test fixtures and synthetic datasets.

Do not share:
- UI component libraries between Android and web (different UI paradigms).
- Platform infrastructure wrappers (camera, storage, background jobs).
- Persistence framework glue code specific to service runtime.

Rule:
- Share business behavior, not platform wiring.

## 8. Split-Ready Strategy (If Monorepo Becomes Multi-Repo)

Future split candidates:
- Repo A: mobile-android
- Repo B: backend platform (api-service + worker-service + db)
- Repo C: web-client
- Repo D: shared contracts (api-contracts + domain schemas)

Preparation rules from day one:
- All cross-module integration must go through versioned API contracts.
- No direct code imports from apps into other apps.
- Shared packages must be semantically versioned.
- Internal APIs documented and backward compatibility policy defined.

Do not split before at least one trigger occurs:
- Team ownership separation.
- Release cadence conflicts.
- CI runtime/complexity pain.
- Security/isolation constraints.

## 9. Domain Model Baseline

Core entities:
- Receipt
- ReceiptImage
- ReceiptItemRaw
- ReceiptItemNormalized
- Product
- Category
- ConsumptionContext
- HouseholdContext
- ProcessingJob

ConsumptionContext (iteration-aware):
- PERSONAL
- SHARED
- FOR_OTHERS

Important behavior:
- Every normalized item must keep traceability to raw source lines.
- Every classification stores confidence score and origin (rule, manual, model).
- Manual correction must override automated classification and remain auditable.

## 10. Data Storage and Migration Path

## 10.1 SQLite Phase

Design constraints:
- Avoid SQLite-only SQL features in domain queries.
- Migrations managed from day one.
- Strict schema versioning.

## 10.2 PostgreSQL Migration Path

Migration readiness:
- Repository pattern in backend to isolate SQL details.
- Dual-engine integration tests run in CI (SQLite mandatory, PostgreSQL optional until migration start).
- Type mappings chosen to be PostgreSQL-safe.

## 10.3 Image Storage

- Store full images on server/PC filesystem.
- Save metadata and path/hash in database.
- Keep immutable originals for model improvement and reprocessing.

## 11. Security Model (Self-Hosted)

MVP security requirements:
- HTTPS required in transport.
- Reverse proxy with TLS termination.
- API request signing token or static key for single-user MVP.
- Secrets in environment variables only.
- Input validation and file type checks on upload.

Iteration 2 readiness:
- Authentication module can be enabled without rewriting domain logic.
- User and household ownership fields already present in schema.

Residency:
- Deployment profile documents support EU or Canada hosting targets.

## 12. API and Inter-Service Communication

Public protocol:
- REST JSON over HTTPS.

Async processing:
- API writes processing jobs to database job table.
- Worker polls and processes with idempotent job handling.

Contract governance:
- OpenAPI spec is source of truth for client-server contracts.
- Breaking changes require version bump and migration notes.

## 13. Taxonomy Strategy (Clarified)

Question clarified:
- Fixed taxonomy means categories are predefined and only changed by code releases.
- Editable taxonomy means categories can be changed from admin/product interfaces without code changes.

Chosen direction:
- Hybrid editable taxonomy.

How it works:
- Start with a seeded base taxonomy (food and non-food).
- Allow editing categories, aliases, and mapping rules.
- Keep versioned taxonomy snapshots to preserve historical analytics consistency.

## 14. Testing Strategy

Goal:
- Strong confidence through behavior-based testing, not arbitrary coverage thresholds.

## 14.1 Test Pyramid

Unit tests (largest layer):
- All public functions in domain and core packages.
- Parsing, normalization, categorization, analytics aggregations.
- Deterministic tests with fixed fixtures.

Integration tests:
- API + DB integration.
- Worker + DB integration.
- File storage integration.
- Contract validation tests (OpenAPI compliance).

Functional tests (end-to-end):
- Ingestion happy path.
- Offline capture then sync.
- Reclassification after manual correction.
- Analytics rendering with realistic data.
- Export flow.

## 14.2 Execution Policy

Every commit:
- Lint + format check.
- Static type checks.
- Full unit test suite.
- Subset functional smoke suite.

Every pull request:
- All commit checks.
- Full functional test suite.
- Contract tests.
- Migration tests.

Nightly or scheduled:
- Extended datasets and long-running scenarios.
- Performance smoke tests.

## 14.3 Quality Gates (No Arbitrary Thresholds)

Mandatory:
- Tests required for changed public behaviors.
- New domain modules require unit tests before merge.
- Bug fixes require at least one regression test.

Informational:
- Coverage report published but not hard-gated by a fixed percent.

## 14.4 Suggested Test Tooling

Backend/worker:
- pytest
- hypothesis (property-based tests for parsers)

Android:
- JUnit + MockK for unit tests
- Espresso or Compose UI tests for functional flows

Web client:
- Vitest for unit
- Playwright for functional/e2e

Contract:
- Schemathesis or Dredd-like API contract validation

## 15. Design Patterns and Code Practices

Recommended patterns:
- Hexagonal architecture (ports/adapters) for backend and worker.
- Repository pattern for persistence abstraction.
- Strategy pattern for parser/classifier implementations.
- Adapter pattern for OCR and LLM providers.
- Factory pattern for selecting parsing pipelines per retailer.
- CQRS-lite separation between write flow (ingestion) and read flow (analytics).

Coding standards:
- Clear module boundaries and dependency direction.
- Pure functions in analytics and normalization where possible.
- Explicit error modeling and retry policies in worker.
- Idempotent processing for re-runs.
- Structured logging with correlation IDs.

## 16. Delivery Plan (Architecture-Only Stage)

Current deliverable:
- Architecture foundation document only.

Next architecture artifacts to add:
- ADR-001: Monorepo baseline and split criteria.
- ADR-002: API protocol and contract governance.
- ADR-003: SQLite to PostgreSQL migration strategy.
- ADR-004: Taxonomy and classification governance.
- ADR-005: Test strategy and CI quality gates.

## 17. Open Decisions

- Final PC client mode for Iteration 1 presentation:
	- Browser-only
	- Browser + packaged desktop wrapper

This document currently recommends browser-first to reduce delivery risk, with desktop packaging later if needed.

---

This architecture is intentionally strict on boundaries and testing so that the project remains clean while still moving quickly.
