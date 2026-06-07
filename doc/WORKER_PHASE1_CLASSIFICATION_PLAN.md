# Worker Phase 1 Classification Slice Plan and Architecture

Status: Proposed then implemented in this branch
Date: 2026-06-07
Scope: Assign taxonomy categories to parsed receipt items using rule-based keyword matching

## Goal

Enrich normalized items with a category_id, a confidence score, and a
classification_origin using the existing taxonomy tree, without coupling the
worker to taxonomy internals.

## Current State

- OCR processor stores parsed items with `category_id=None`, `confidence` from
  the parser, and `classification_origin="rule"`.
- `taxonomy-core` has a full node model, loader, and in-memory repository.
- No classifier exists yet.

## Target Architecture

### 1) Classifier in `taxonomy-core`

Add a `KeywordClassifier` to `taxonomy-core`:
- Builds a keyword → category-id map from taxonomy node names and slugs at
  construction time.
- Exposes one method: `classify(name: str) -> ClassificationResult`.
- Returns matched category_id + confidence, or a `non-food-other` fallback.

Why taxonomy-core owns this: classifier logic depends only on the taxonomy tree
and pure string matching.  No SQLAlchemy, no worker internals.

```
ClassificationResult(category_id: str, confidence: float, origin: str)
```

### 2) Worker Integration (Dependency Injection)

`OcrProcessor` receives a `KeywordClassifier` dependency.
On each parsed line the processor:
1. Calls `classifier.classify(parsed.normalized_name)`.
2. Writes `category_id`, `confidence`, `classification_origin` from the result.

Why: keeps processor orchestration-focused and open to future classifier swap.

### 3) Keyword Matching Strategy

Expand each taxonomy node into keywords:
- node.name words (lowercased, split by space and `/`)
- slug segments (split by `-`)

For each item name:
1. Tokenise name by whitespace.
2. Match tokens against keyword index.
3. First match wins (leaves preferred over parents because they are indexed last
   and later entries overwrite in the keyword map — leaves are deeper in the tree
   so they appear later in depth-first iteration).
4. No match → fallback to `non-food-other` with confidence 0.1.

### Design Patterns Used

| Pattern | Where | Why |
|---------|-------|-----|
| Strategy | `KeywordClassifier` behind an abstract `BaseClassifier` | Allows future ML/LLM classifier swap without touching OcrProcessor |
| Factory | Classifier construction in `processor_factory.py` | Keeps classifier wiring out of caller code |
| Dependency Injection | `OcrProcessor.__init__` receives classifier | Enables test doubles |

## Testing Plan

### Unit: `taxonomy-core`

- Classifier returns expected category for a known keyword.
- Classifier returns `non-food-other` fallback for unknown name.
- Classifier matches partial token in a multi-word name.
- Classifier is case-insensitive.
- Classifier returns `origin="rule"` for all results.

### Integration: `worker-service`

- OcrProcessor writes non-null category_id from classifier results.
- OcrProcessor respects injected classifier (fake in tests, real in factory).

## Acceptance Criteria

- All items leaving the processor have a `category_id` (fallback if no match).
- Full test suite green.
- `uv run pytest -q` in repo root passes.

## Deferred

- Alias / synonym mapping per category.
- ML/LLM-backed classifier strategy.
- User-defined classification overrides.
- Confidence threshold routing (low-confidence → manual queue).
