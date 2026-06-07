from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from taxonomy_core.models import TaxonomyNode

_DEFAULT_TAXONOMY_PATH = Path(__file__).parent.parent.parent / "data" / "base_taxonomy.json"


class TaxonomyLoader:
    """
    Loads a taxonomy tree from a JSON file.
    Static factory methods allow callers to load without knowing file locations.
    """

    @staticmethod
    def load_default() -> list[TaxonomyNode]:
        """Load the built-in base taxonomy."""
        return TaxonomyLoader.load_from_file(_DEFAULT_TAXONOMY_PATH)

    @staticmethod
    def load_from_file(path: Path) -> list[TaxonomyNode]:
        """Load taxonomy from any JSON file following the base_taxonomy.json schema."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return TaxonomyLoader._parse_nodes(data["categories"], parent_id=None)

    @staticmethod
    def _parse_nodes(
        items: list[dict[str, Any]], parent_id: str | None
    ) -> list[TaxonomyNode]:
        nodes: list[TaxonomyNode] = []
        for item in items:
            node = TaxonomyNode(
                id=item["id"],
                name=item["name"],
                slug=item["slug"],
                parent_id=parent_id,
                is_food=item["is_food"],
            )
            node.children = TaxonomyLoader._parse_nodes(
                item.get("children", []), parent_id=item["id"]
            )
            nodes.append(node)
        return nodes
