from __future__ import annotations

import re

from taxonomy_core.classifier import BaseClassifier, ClassificationResult
from taxonomy_core.models import TaxonomyNode

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_FALLBACK_CATEGORY_ID = "non-food-other"
_FALLBACK_CONFIDENCE = 0.1


class KeywordClassifier(BaseClassifier):
    """
    Rule-based classifier that maps item name tokens to taxonomy categories.

    Strategy pattern: implements BaseClassifier so it can be swapped for an
    ML or LLM classifier without touching any caller code.

    Build phase: expands every taxonomy node into keyword tokens derived from
    its name and slug.  Leaves are indexed after parents (depth-first), so a
    leaf keyword overwrites its parent's entry — giving leaf-level precision.

    Classify phase: tokenises the item name and returns the first keyword hit.
    Falls back to `non-food-other` when no token matches.
    """

    def __init__(self, nodes: list[TaxonomyNode]) -> None:
        self._index: dict[str, str] = {}
        self._build_index(nodes)

    def classify(self, name: str) -> ClassificationResult:
        tokens = _TOKEN_RE.findall(name.lower())
        for token in tokens:
            category_id = self._index.get(token)
            if category_id:
                return ClassificationResult(
                    category_id=category_id,
                    confidence=0.7,
                    origin="rule",
                )
        return ClassificationResult(
            category_id=_FALLBACK_CATEGORY_ID,
            confidence=_FALLBACK_CONFIDENCE,
            origin="rule",
        )

    def _build_index(self, nodes: list[TaxonomyNode]) -> None:
        for node in nodes:
            for keyword in self._keywords_for(node):
                self._index[keyword] = node.id
            self._build_index(node.children)

    @staticmethod
    def _keywords_for(node: TaxonomyNode) -> list[str]:
        keywords: list[str] = []
        for word in _TOKEN_RE.findall(node.name.lower()):
            keywords.append(word)
        for segment in node.slug.split("-"):
            segment = segment.strip()
            if segment:
                keywords.append(segment)
        return keywords
