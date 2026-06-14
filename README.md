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

# Dev
```bash
# Install uv (once)
pip install uv

# From repo root: install everything
uv sync --all-packages

# Run all unit tests
uv run --package domain-models  pytest packages/domain-models/tests -v
uv run --package taxonomy-core  pytest packages/taxonomy-core/tests  -v
uv run --package persistence    pytest packages/persistence/tests    -v
uv run --package api-service    pytest apps/api-service/tests        -v
uv run --package worker-service pytest apps/worker-service/tests     -v

# Run services locally (no Docker)
cp .env.example .env
uv run --package api-service uvicorn api_service.main:app --reload
uv run --package worker-service python -m worker_service.main

# Or with Docker
docker compose -f infra/docker/docker-compose.yml up --build
```