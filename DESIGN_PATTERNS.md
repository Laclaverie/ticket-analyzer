# Design Patterns Reference

This document records which design patterns are applied in each module,
why each was chosen, and what constraints come from them.
It is a living document: update it when a pattern is added, changed, or removed.

---

## Monorepo Layout

```
packages/
  domain-models/     pure Python domain
  taxonomy-core/     category management
  persistence/       SQLAlchemy ORM shared between apps
  parsing-core/      parsing and normalization (Phase 2)
  analytics-core/    metrics and aggregations (Phase 2+)
  test-fixtures/     shared test datasets

apps/
  api-service/       HTTP API
  worker-service/    async job processor
  mobile-android/    Android client
  web-client/        PC browser client
```

Dependency direction rule:
- packages can depend on other packages.
- apps can depend on packages.
- apps must NOT depend on other apps.
- packages must NOT depend on apps.

---

## packages/domain-models

### Pattern: Value Object

All domain entities (Receipt, ReceiptItemRaw, ReceiptItemNormalized, Category,
ProcessingJob) are implemented as frozen Python dataclasses.

Why:
- Domain concepts have identity and meaning, not behaviour.
- Immutability prevents accidental mutations across layers.
- Invariants (non-empty id, valid currency code, confidence in [0,1]) are
  enforced in `__post_init__`, making illegal states unrepresentable.

Constraint:
- This package has zero framework dependencies. It must never import SQLAlchemy,
  FastAPI, or any third-party library.
- Any framework-specific representation lives in the app layer, not here.

---

## packages/taxonomy-core

### Pattern: Repository (read-only, in-memory)

`TaxonomyRepository` builds a flat index (by id, by slug) from a loaded tree
of `TaxonomyNode` objects. All lookups are O(1).

Why:
- Separates how categories are stored (JSON file, future DB) from how they are
  queried by the rest of the code.
- Open for extension: load from a database, a remote source, or a test fixture
  by swapping the loader without changing the repository.

### Pattern: Composite

`TaxonomyNode` has a `children: list[TaxonomyNode]` field, forming a recursive
tree. `all_descendants()` traverses the subtree uniformly.

Why:
- The category hierarchy is naturally recursive (food > fresh food > dairy).
- Leaf nodes and branch nodes are treated identically by consumers.

### Pattern: Static Factory Method

`TaxonomyLoader.load_default()` and `TaxonomyLoader.load_from_file(path)` are
static methods. Callers do not need to know how the JSON is located or parsed.

Why:
- Keeps loading logic in one place.
- Makes tests trivially simple: pass a custom path without any configuration.

---

## packages/persistence

### Pattern: Data Mapper (ORM as mapper, not Active Record)

SQLAlchemy ORM models (`ReceiptORM`, `ProcessingJobORM`, etc.) are kept strictly
separate from domain models (`Receipt`, `ProcessingJob`).

Why:
- Domain objects are framework-agnostic (see domain-models above).
- Persistence concerns (column types, foreign keys, lazy loading) do not leak
  into business logic.
- Enables switching the ORM or the database engine without touching domain code.

Constraint:
- ORM models live in `packages/persistence`, shared between `api-service` and
  `worker-service` to avoid duplicating table definitions.
- Mapping between ORM and domain objects is the responsibility of each app's
  Repository layer, not this package.

---

## apps/api-service

### Pattern: Hexagonal Architecture (Ports and Adapters)

The application is divided into three rings:
- Core: domain models and business rules (packages/).
- Ports: interfaces that the core exposes (Repository protocols).
- Adapters: concrete implementations (SQLAlchemy repositories, FastAPI routers).

Why:
- Business logic is testable without a running HTTP server or a real database.
- Adding a new transport (gRPC, CLI) means writing a new adapter, not touching
  the core.

### Pattern: Repository

`ReceiptRepository` and `JobRepository` in `api-service` are the only classes
allowed to execute SQL. They translate between ORM objects and domain objects.
Callers work exclusively with domain objects.

Why:
- SQL details are isolated. Changing a query does not ripple into service logic.
- Repository interfaces can be replaced with in-memory fakes in tests (no DB
  setup needed for unit tests of service logic).

### Pattern: Dependency Injection (FastAPI Depends)

All dependencies (database session, settings, repositories) are injected via
FastAPI's `Depends` mechanism.

Why:
- Tests override dependencies trivially without monkey-patching.
- Each component declares its own needs explicitly (explicit is better than
  implicit).

### Pattern: Service Layer

`IngestionService` orchestrates the upload flow: file storage, receipt creation,
image record, job enqueue. It has no knowledge of HTTP or SQL.

Why:
- Routers stay thin (parse request, call service, return response).
- Service logic is tested independently from HTTP concerns.

Constraint:
- Services must not commit transactions. Transaction boundaries are owned by
  the router (one request = one transaction).

---

## apps/worker-service

### Pattern: Strategy (processor dispatch)

`BaseProcessor` is an abstract base class defining the `process(job_id)` contract.
Each concrete processor (currently `StubProcessor`, later `OcrProcessor`) is a
strategy that can be swapped at construction time.

Why:
- Adding a new processing strategy (Phase 1: real OCR) requires only a new
  subclass; the poller and job repository do not change.
- Open/Closed Principle: open for extension (new strategies), closed for
  modification (existing code unchanged).

### Pattern: Template Method (job lifecycle)

`JobPoller.poll_once()` defines the fixed lifecycle:
1. Find pending jobs.
2. Dispatch to processor.
3. Mark completed or failed.

The step that varies (step 2) is delegated to the injected `BaseProcessor`.

Why:
- The lifecycle is stable. Only the processing behaviour changes per phase.
- Error handling and status transitions are centralised in one place.

### Pattern: Repository

`JobRepository` in `worker-service` is the only component allowed to read/write
`processing_jobs`. It translates ORM objects to domain objects, mirrors the
pattern in `api-service`.

Constraint:
- Repositories do not commit. `JobPoller` owns transaction boundaries.

---

## apps/web-client and apps/mobile-android

Patterns will be documented when implementation starts.

Candidates:
- MVVM for both clients (ViewModel owns state, View is dumb).
- Repository pattern for remote data access (mirrors backend).
- Observer/Flow for reactive data updates.

---

## Cross-Cutting: Open/Closed Principle

Enforced at these extension points:

| Extension point        | How to extend                          | What not to touch |
|------------------------|----------------------------------------|-------------------|
| New processor type     | Subclass `BaseProcessor`               | `JobPoller`       |
| New taxonomy source    | New `TaxonomyLoader` method or subclass| `TaxonomyRepository` |
| New API endpoint       | New router file + register in `main.py`| Existing routers  |
| New ORM model          | New file in `persistence/models/`      | Existing models   |
| New export format      | New exporter class (Phase 4)           | Existing exporters|

---

## Cross-Cutting: File Size and Responsibility

Hard rules:
- No file exceeds 300 lines. If approaching that limit, split by responsibility.
- Each class has one reason to change.
- No business logic in routers or ORM models.
- No database code in services or domain models.
