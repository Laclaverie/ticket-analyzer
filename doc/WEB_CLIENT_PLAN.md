# Web Client Plan

Status: Proposed
Date: 2026-06-07
Scope: browser-first desktop client for receipts, analytics, and export

## Goal

Deliver the first PC-facing UI slice now that the backend is stable: a desktop-first browser app that can inspect receipts, drill into a receipt, and export visible data.

## First Slice

- Connect to the existing FastAPI backend.
- Show a receipt list with status and totals.
- Show analytics summaries for category spend and monthly spend.
- Show receipt detail with extracted items.
- Provide a CSV export for the currently loaded list.

## Constraints

- No authentication for MVP.
- No client-side business calculations beyond presentation and export formatting.
- Keep the client shell isolated so a later Tauri wrapper can reuse it.

## Implementation Notes

- Use a small Vite + React + TypeScript app.
- Prefer direct fetch calls to the public API.
- Use mock fallback data when the backend is unavailable so the UI still renders during development.
- Keep layout desktop-first but responsive.

## Done When

- The web client opens in the browser.
- Receipt data and analytics are visible.
- A receipt can be selected to inspect its items.
- CSV export works on the visible receipt list.