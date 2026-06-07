# MVP Plan — First End-to-End

Status: Active reference
Date: 2026-06-07

## Guiding Principle

The thinnest vertical slice that works entirely end-to-end:
1. Take a receipt photo on phone.
2. Upload it to the server.
3. See processed and categorized items.
4. See one basic analytics view on phone and on PC.

Nothing else. No auth, no multi-user, no budget features, no advanced analytics.

---

## Phase 0 — Infrastructure Baseline

Goal: everything runs locally end to end.

Tasks:
- [ ] SQLite schema v1 with migrations (receipts, receipt_items_raw, receipt_items_normalized, categories, processing_jobs).
- [ ] FastAPI skeleton with health endpoint and one upload endpoint stub.
- [ ] Worker skeleton that polls processing_jobs and logs them.
- [ ] Seed base taxonomy (food/non-food with 10-15 subcategories).
- [ ] Docker Compose that starts API + worker together.

Done when:
> You can POST a file to the API and see a job created in the database.

---

## Phase 1 — Ingestion Pipeline

Goal: a receipt image goes in and raw OCR text comes out.

Tasks:
- [ ] Upload endpoint stores image on filesystem and raw metadata in DB.
- [ ] Worker picks up job and runs server-side OCR (Tesseract as default adapter).
- [ ] Raw text saved in receipt_items_raw.
- [ ] Job marked complete with raw output.

Done when:
> You upload a receipt photo and can query the raw OCR text back from the API.

---

## Phase 2 — Parsing and Classification

Goal: raw OCR text becomes structured line items with categories.

Tasks:
- [ ] Line item extractor (regex + heuristics) splits OCR text into name/quantity/price triplets.
- [ ] Normalization rules clean product names.
- [ ] Rule-based classifier maps normalized names to taxonomy.
- [ ] Confidence score and classification origin stored per item (rule/manual).
- [ ] Unit tests for parser and classifier using packages/test-fixtures.

Done when:
> You upload a receipt and can query back structured items with category assignments.

---

## Phase 3 — Android MVP Client

Goal: capture and view on phone.

Tasks:
- [ ] Camera screen using CameraX.
- [ ] On-device OCR preview using Google ML Kit (show extracted text before upload).
- [ ] Upload flow with offline queue (store locally, sync when online).
- [ ] Receipt list screen showing status: pending / processed.
- [ ] Receipt detail screen showing items with categories.
- [ ] One analytics screen: category donut chart for current month.

Done when:
> You take a photo, see the items parsed, and see one chart on the phone.

---

## Phase 4 — Web Client MVP

Goal: PC view of the same data.

Tasks:
- [ ] Receipt list with date and store.
- [ ] Receipt detail showing item list.
- [ ] Category spending breakdown by month as a bar chart.
- [ ] CSV export for all items.

Done when:
> You open the browser on PC, see your receipts and one analytics chart, and export data to CSV.

---

## Full End-to-End Definition of Done

- [ ] Android captures receipt offline and syncs when online.
- [ ] Worker processes and classifies items.
- [ ] Mobile shows item list + one analytics chart.
- [ ] PC web shows receipt list + category breakdown + CSV export.
- [ ] All public business logic in packages/ covered by unit tests.
- [ ] One functional smoke test covers the full ingestion path end to end.

---

## Explicitly Out of Scope for MVP

- Authentication and user accounts.
- Personal / shared / for-others consumption contexts (Iteration 2).
- LLM-assisted classification.
- Advanced trend analytics.
- Desktop packaging (Tauri).
- Observability dashboards.
- Multi-store normalizations.

---

## Implementation Order

| Phase | Scope                     | Starts when         |
|-------|---------------------------|---------------------|
| 0     | Infrastructure baseline   | Now                 |
| 1     | Ingestion pipeline        | Phase 0 done        |
| 2     | Parsing and classification| Phase 1 done        |
| 3     | Android MVP client        | Phase 2 done        |
| 4     | Web client MVP            | Phase 2 done        |

Phases 3 and 4 can run in parallel once Phase 2 is complete.

---

## Module Ownership Per Phase

| Phase | Primary modules                                           |
|-------|-----------------------------------------------------------|
| 0     | db/migrations, apps/api-service, apps/worker-service, packages/taxonomy-core |
| 1     | apps/api-service, apps/worker-service                     |
| 2     | packages/parsing-core, packages/taxonomy-core, packages/domain-models, packages/test-fixtures |
| 3     | apps/mobile-android                                       |
| 4     | apps/web-client                                           |

---

## Related Documents

- Architecture baseline: [doc/ARCHITECTURE.md](ARCHITECTURE.md)
- ADR set: [doc/ADR/README.md](ADR/README.md)
- ADR-006: full increment roadmap and risk register
