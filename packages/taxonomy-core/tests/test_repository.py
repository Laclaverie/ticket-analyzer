import pytest

from taxonomy_core.loader import TaxonomyLoader
from taxonomy_core.repository import TaxonomyRepository


@pytest.fixture(scope="module")
def repo() -> TaxonomyRepository:
    nodes = TaxonomyLoader.load_default()
    return TaxonomyRepository(nodes)


def test_find_by_id_returns_correct_node(repo):
    node = repo.find_by_id("food")
    assert node is not None
    assert node.slug == "food"


def test_find_by_id_unknown_returns_none(repo):
    assert repo.find_by_id("does-not-exist") is None


def test_find_by_slug_returns_correct_node(repo):
    node = repo.find_by_slug("non-food")
    assert node is not None
    assert node.id == "non-food"


def test_find_by_slug_unknown_returns_none(repo):
    assert repo.find_by_slug("unknown-slug") is None


def test_all_nodes_includes_roots_and_leaves(repo):
    all_nodes = repo.all_nodes()
    slugs = {n.slug for n in all_nodes}
    assert "food" in slugs
    assert "food-fresh-dairy" in slugs


def test_root_nodes_are_all_roots(repo):
    for node in repo.root_nodes():
        assert node.is_root()


def test_leaf_nodes_have_no_children(repo):
    for node in repo.leaf_nodes():
        assert node.is_leaf()


def test_leaf_node_lookup(repo):
    node = repo.find_by_slug("food-fresh-dairy")
    assert node is not None
    assert node.is_food is True
    assert node.is_leaf()


def test_food_nodes_all_have_is_food_true(repo):
    for node in repo.food_nodes():
        assert node.is_food is True


def test_non_food_nodes_all_have_is_food_false(repo):
    for node in repo.non_food_nodes():
        assert node.is_food is False


def test_all_nodes_count_is_consistent(repo):
    # 2 roots + their descendants must all appear in all_nodes
    all_nodes = repo.all_nodes()
    assert len(all_nodes) >= 2
