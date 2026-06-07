from __future__ import annotations

from taxonomy_core.models import TaxonomyNode


class TaxonomyRepository:
    """
    In-memory index over a loaded taxonomy tree.
    All lookups are O(1).

    Open for extension: subclass and override lookup methods to add
    fuzzy matching, alias resolution, or persistence-backed lookups.
    """

    def __init__(self, nodes: list[TaxonomyNode]) -> None:
        self._by_id: dict[str, TaxonomyNode] = {}
        self._by_slug: dict[str, TaxonomyNode] = {}
        self._index(nodes)

    def _index(self, nodes: list[TaxonomyNode]) -> None:
        for node in nodes:
            self._by_id[node.id] = node
            self._by_slug[node.slug] = node
            self._index(node.children)

    def find_by_id(self, node_id: str) -> TaxonomyNode | None:
        return self._by_id.get(node_id)

    def find_by_slug(self, slug: str) -> TaxonomyNode | None:
        return self._by_slug.get(slug)

    def all_nodes(self) -> list[TaxonomyNode]:
        return list(self._by_id.values())

    def root_nodes(self) -> list[TaxonomyNode]:
        return [n for n in self._by_id.values() if n.is_root()]

    def leaf_nodes(self) -> list[TaxonomyNode]:
        return [n for n in self._by_id.values() if n.is_leaf()]

    def food_nodes(self) -> list[TaxonomyNode]:
        return [n for n in self._by_id.values() if n.is_food]

    def non_food_nodes(self) -> list[TaxonomyNode]:
        return [n for n in self._by_id.values() if not n.is_food]
