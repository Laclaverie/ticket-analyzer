from taxonomy_core.classifier import ClassificationResult
from taxonomy_core.keyword_classifier import KeywordClassifier
from taxonomy_core.loader import TaxonomyLoader


def _classifier() -> KeywordClassifier:
    return KeywordClassifier(TaxonomyLoader.load_default())


def test_classify_known_food_keyword():
    # 'dairy' and 'eggs' are both keywords derived from the Dairy & Eggs node
    result = _classifier().classify("dairy")
    assert result.category_id == "food-fresh-dairy"
    assert result.confidence > 0.0
    assert result.origin == "rule"


def test_classify_eggs_keyword():
    result = _classifier().classify("eggs")
    assert result.category_id == "food-fresh-dairy"


def test_classify_known_non_food_keyword():
    # 'hygiene' is a keyword from the Personal Hygiene node
    result = _classifier().classify("hygiene")
    assert result.category_id == "non-food-hygiene"
    assert result.origin == "rule"


def test_classify_fallback_for_unknown_name():
    result = _classifier().classify("xyzzy unknownitem")
    assert result.category_id == "non-food-other"
    assert result.confidence == 0.1


def test_classify_is_case_insensitive():
    c = _classifier()
    lower = c.classify("dairy")
    upper = c.classify("DAIRY")
    mixed = c.classify("Dairy")
    assert lower.category_id == upper.category_id == mixed.category_id


def test_classify_matches_token_in_multi_word_name():
    # 'bakery' maps to food-fresh-bread; 'bread' also maps there
    result = _classifier().classify("fresh sourdough bakery")
    assert result.category_id == "food-fresh-bread"


def test_classify_returns_classification_result_type():
    result = _classifier().classify("apple")
    assert isinstance(result, ClassificationResult)


def test_classify_confidence_is_valid_range():
    c = _classifier()
    for name in ["dairy", "beverages", "hygiene", "xyzzy"]:
        result = c.classify(name)
        assert 0.0 <= result.confidence <= 1.0


def test_classify_origin_is_always_rule():
    c = _classifier()
    for name in ["dairy", "beverages", "hygiene", "xyzzy"]:
        assert c.classify(name).origin == "rule"
