import pytest
from pathlib import Path

from taxonomy_core.loader import TaxonomyLoader


def test_load_default_returns_nodes():
    nodes = TaxonomyLoader.load_default()
    assert len(nodes) > 0


def test_root_nodes_have_no_parent():
    nodes = TaxonomyLoader.load_default()
    for node in nodes:
        assert node.parent_id is None


def test_default_taxonomy_has_food_and_nonfood():
    nodes = TaxonomyLoader.load_default()
    slugs = {n.slug for n in nodes}
    assert "food" in slugs
    assert "non-food" in slugs


def test_child_nodes_carry_parent_id():
    nodes = TaxonomyLoader.load_default()
    for root in nodes:
        for child in root.children:
            assert child.parent_id == root.id


def test_all_nodes_have_non_empty_id_and_slug():
    def check(nodes):
        for n in nodes:
            assert n.id, f"Empty id for node {n.name}"
            assert n.slug, f"Empty slug for node {n.name}"
            check(n.children)

    check(TaxonomyLoader.load_default())


def test_food_nodes_have_is_food_true():
    nodes = TaxonomyLoader.load_default()
    food_root = next(n for n in nodes if n.slug == "food")
    assert food_root.is_food is True
    for child in food_root.all_descendants():
        assert child.is_food is True


def test_non_food_nodes_have_is_food_false():
    nodes = TaxonomyLoader.load_default()
    non_food = next(n for n in nodes if n.slug == "non-food")
    assert non_food.is_food is False
    for child in non_food.all_descendants():
        assert child.is_food is False


def test_load_from_file_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        TaxonomyLoader.load_from_file(Path("/nonexistent/taxonomy.json"))
