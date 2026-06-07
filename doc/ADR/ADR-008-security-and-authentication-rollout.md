# ADR-008 - Security and Authentication Rollout

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

Iteration 1 is single-user and self-hosted with no full authentication requirement.
However, secure communication is required from day one.
Iteration 2 introduces shared consumption contexts and potential multi-user semantics.

## Decision

Use phased security architecture:
- Phase A (Iteration 1): transport security + service-level access control, no user accounts.
- Phase B (Iteration 2): introduce authentication and ownership-aware authorization.

Phase A controls:
- HTTPS mandatory.
- Reverse proxy TLS termination.
- API token or signed client key for trusted single-user clients.
- Input validation and upload hardening.
- Secrets managed through environment variables.

Phase B controls:
- User identity and session/token management.
- Authorization policy bound to household and consumption contexts.
- Audit events for access-sensitive operations.

## Needs Addressed

- Keep MVP simple while still secure.
- Avoid re-architecture when adding multi-user capabilities.
- Ensure data handling remains acceptable for self-hosted private usage.

## Risks

1. Security debt if MVP shortcuts become permanent.
2. Schema gaps that complicate user/household ownership introduction.
3. Misconfigured TLS in self-hosted deployments.

## Mitigations

1. Define auth extension points in API and domain now.
2. Include nullable owner/household fields from early schema versions.
3. Provide deployment checklists and automated startup validation.

## Increment Plan

Increment 1:
- Enforce HTTPS and token-protected API access.
- Store and rotate secrets through environment configuration.
- Log security-relevant events (failed uploads, invalid signatures).

Increment 2:
- Add identity provider abstraction and authentication flows.
- Enable authorization checks by ownership and context.
- Add integration tests for auth and policy enforcement.

Increment 3:
- Harden with optional MFA support and session management improvements.
- Add security smoke tests to CI and periodic vulnerability checks.

## Revisit Triggers

- Exposure beyond trusted home network.
- Multi-user onboarding start.
- Regulatory/privacy expectation increase.

## Exit Criteria

- MVP traffic is encrypted and access-controlled.
- Iteration 2 can enable auth without domain model rewrite.
- Authorization behavior is verified by automated tests.
