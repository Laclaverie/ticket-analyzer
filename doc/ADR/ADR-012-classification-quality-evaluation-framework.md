# ADR-012 - Classification Quality Evaluation Framework

Status: Accepted
Date: 2026-06-07
Owners: Project maintainers

## Context

Classification quality directly affects user trust in consumption analytics.
The system will combine rule-based matching, optional model-assisted matching, and manual corrections.
Without explicit evaluation, quality regressions may remain unnoticed.

## Decision

Adopt a measurable evaluation framework with versioned datasets, quality metrics, and release gates.

Evaluation components:
- Gold dataset: manually validated receipt items across representative stores/categories.
- Shadow dataset: recent real-world receipts sampled for drift detection.
- Offline benchmark pipeline: runs each classifier version against datasets.

Quality dimensions:
- Category assignment correctness.
- Product normalization consistency.
- Confidence calibration reliability.
- Coverage rate (fraction of items classified above acceptable confidence).

Metric policy:
- Track precision, recall, F1 per major category family.
- Track unknown/unclassified rate.
- Track manual override rate after initial classification.

## Needs Addressed

- Reliable analytics outputs.
- Controlled improvement when classification logic changes.
- Early detection of drift by store or category.

## Risks

1. Gold dataset bias toward a few stores.
2. Overfitting to benchmark while production quality degrades.
3. Confidence scores become non-comparable across model/rule versions.

## Mitigations

1. Refresh dataset composition each increment.
2. Include shadow dataset monitoring and manual sampling.
3. Version confidence semantics and publish calibration notes.

## Increment Plan

Increment 1:
- Build first gold dataset from current receipt corpus.
- Define baseline metrics and reporting format.

Increment 2:
- Add CI benchmark job for classifier changes.
- Add blocking guardrail for severe metric regressions.

Increment 3:
- Add store-specific drift monitors and taxonomy-aware dashboards.
- Introduce active-learning loop from manual corrections.

## Revisit Triggers

- Rising manual correction rate.
- Significant drop in category-level precision/recall.
- Addition of new stores with materially different receipt formats.

## Exit Criteria

- Classification changes are benchmarked before release.
- Quality trend is visible across versions.
- Regression handling is operationalized with clear rollback paths.
