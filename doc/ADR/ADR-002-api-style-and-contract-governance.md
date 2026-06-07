# ADR-002 - API Style and Contract Governance

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

Clients (Android and PC) and services (API and worker) must interoperate with low friction.
The project needs clear evolution rules to avoid breaking changes as features expand.

## Decision

Use REST/JSON over HTTPS for public client-server communication.

Contract source of truth:
- OpenAPI specification
- JSON Schema for request/response validation

Versioning policy:
- Non-breaking changes: additive fields only
- Breaking changes: new API version and migration note

## Needs Addressed

- Simple and predictable client integration.
- Contract testability and schema validation.
- Ease of onboarding and debugging.

## Risks

1. Contract drift between implementation and documentation.
2. Inconsistent error modeling across endpoints.
3. Hidden breaking changes from loosely validated payloads.

## Mitigations

1. Validate payloads at runtime against schema.
2. Add contract tests in CI for all public endpoints.
3. Define common error envelope and error codes.

## Increment Plan

Increment 1:
- Define core ingestion and analytics endpoints in OpenAPI.
- Implement schema validation middleware.

Increment 2:
- Generate client stubs for Android and web.
- Add backward compatibility checks in CI.

Increment 3:
- Add version deprecation strategy with migration guides.

## Exit Criteria

- OpenAPI spec matches deployed endpoints.
- Contract tests run on each pull request.
- No undocumented public endpoint behavior.
