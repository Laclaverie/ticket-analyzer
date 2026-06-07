from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    category_id: str
    confidence: float
    origin: str


class BaseClassifier(ABC):
    """
    Strategy interface for item classification.

    Implementations may use keyword rules, ML models, or LLM calls.
    The interface is intentionally minimal: one method, pure value result.
    """

    @abstractmethod
    def classify(self, name: str) -> ClassificationResult:
        """Return a ClassificationResult for the given normalised item name."""
