from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaxonomyNode:
    """
    A single node in the category hierarchy.
    Implements the Composite pattern: leaf nodes and branch nodes are treated identically.
    """

    id: str
    name: str
    slug: str
    parent_id: str | None
    is_food: bool
    children: list[TaxonomyNode] = field(default_factory=list)

    def is_root(self) -> bool:
        return self.parent_id is None

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def all_descendants(self) -> list[TaxonomyNode]:
        """Return all descendants in depth-first order."""
        result: list[TaxonomyNode] = []
        for child in self.children:
            result.append(child)
            result.extend(child.all_descendants())
        return result
