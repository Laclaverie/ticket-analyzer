# ADR-007 - PC Client Delivery Mode

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

PC access is required for deeper analysis and export.
Two candidate modes were considered:
- Browser web app only
- Browser web app plus packaged desktop wrapper

The project is early stage and optimized for fast iterations with clean architecture.

## Decision

Adopt browser-first for Iteration 1, with optional desktop packaging as an Increment 3 enhancement.

Implementation direction:
- Build one web client optimized for desktop usage.
- Keep packaging boundary clean so Tauri wrapper can be added later without rewriting business logic.

## Needs Addressed

- Fast delivery of PC analytics and export.
- Low operational and release complexity at project start.
- Preserved optionality for desktop-native distribution later.

## Risks

1. Browser UX may feel less native for desktop-heavy usage.
2. File-system export and local integration can be less direct in browser mode.
3. Delayed packaging work might create retrofitting effort later.

## Mitigations

1. Design web UX with desktop-first information density and keyboard shortcuts.
2. Keep export flows explicit and robust (CSV/JSON with deterministic schemas).
3. Isolate client business logic from shell integration points.

## Increment Plan

Increment 1:
- Deliver browser web app with analytics and export.
- Validate responsiveness and usability on target desktop environment.

Increment 2:
- Add optional local cache and improved desktop ergonomics in browser.

Increment 3:
- If needed, package via Tauri using same web app artifacts.

## Revisit Triggers

- Repeated user pain around browser limitations.
- Need for tighter OS integration.
- Requirement for offline desktop analytics.

## Exit Criteria

- PC workflows (analysis + export) are complete in browser mode.
- Desktop packaging can be introduced with minimal code changes.
