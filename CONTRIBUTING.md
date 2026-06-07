# Contributing

## Branching

- Use short-lived feature branches.
- Keep pull requests focused on one concern.
- Reference ADRs when a change impacts architecture.

## Coding Rules

- Respect module boundaries from ADR-001.
- Keep domain logic in packages, not in UI layers.
- Prefer explicit, typed interfaces for contracts.

## Tests and Quality Gates

Every commit should pass:
- lint and formatting checks
- static type checks
- unit tests
- functional smoke tests

Every pull request should pass:
- full functional tests
- API contract tests
- migration tests

## Definition of Done

- Public behavior changes are covered by tests.
- Bug fixes include at least one regression test.
- Documentation is updated when behavior or architecture changes.
