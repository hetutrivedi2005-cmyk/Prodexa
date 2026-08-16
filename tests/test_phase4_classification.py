import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.understanding.taxonomy_builder import TaxonomyBuilder
from src.understanding.classifier import TaxonomyClassifier


@pytest.fixture(scope="module")
def setup_taxonomy():
    builder = TaxonomyBuilder()
    df_tax = builder.build_taxonomy()
    builder.validate_taxonomy(df_tax)
    return builder


@pytest.fixture
def classifier(setup_taxonomy):
    return TaxonomyClassifier()


def test_exact_product_type_match(classifier):
    res = classifier.classify_product(product_type="Sanding Belt", part_desc="Diablo 1/2 in x 18 in Sanding Belt 6pc")
    assert res["category_id"] == "ABR_BELT_SANDING"
    assert res["category_name"] == "Sanding Belts"
    assert res["classification_status"] == "classified"
    assert res["classification_method"] == "rule_exact"
    assert res["classification_confidence"] == 1.0


def test_case_insensitive_match(classifier):
    res = classifier.classify_product(product_type="sanding belt")
    assert res["category_id"] == "ABR_BELT_SANDING"
    assert res["classification_method"] in ["rule_exact", "rule_normalized"]


def test_normalized_product_type_match(classifier):
    res = classifier.classify_product(product_type="Cut Off Disc")
    assert res["category_id"] == "ABR_DISC_CUT"
    assert res["classification_method"] in ["rule_exact", "rule_normalized"]


def test_keyword_match(classifier):
    res = classifier.classify_product(part_desc="2761-20 Milw M18 1/4 Hex Hydraulic Driver")
    assert res["category_id"] == "PWR_DRILL_IMP"
    assert res["classification_method"] == "rule_keyword"
    assert res["classification_confidence"] > 0.80


def test_alias_match(classifier):
    res = classifier.classify_product(part_desc="Heavy Duty Sanding Band 1/2 x 18")
    assert res["category_id"] == "ABR_BELT_SANDING"
    assert res["classification_status"] == "classified"


def test_specific_category_beats_parent_category(classifier):
    res = classifier.classify_product(product_type="Sanding Belt", part_desc="Sanding Belt 6pc")
    # Level 3 specific category (ABR_BELT_SANDING) must be chosen over Level 2 parent (ABR_BELT)
    assert res["hierarchy_level"] == 3
    assert res["category_id"] == "ABR_BELT_SANDING"


def test_llm_chooses_valid_candidate(classifier):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"category_id": "ABR_BELT_SANDING", "confidence": 0.75}'
    mock_client.models.generate_content.return_value = mock_response

    llm_classifier = TaxonomyClassifier(client=mock_client)
    res = llm_classifier.classify_product(part_desc="Ambiguous Abrasive Item XYZ")

    if res["category_id"]:
        assert res["category_id"] in classifier.categories_by_id


def test_llm_attempts_invalid_category_rejected(classifier):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"category_id": "INVALID_HALLUCINATED_CAT_999", "confidence": 0.99}'
    mock_client.models.generate_content.return_value = mock_response

    llm_classifier = TaxonomyClassifier(client=mock_client)
    res = llm_classifier.classify_product(part_desc="Completely Unknown Item 99999")

    # Invalid hallucinated category ID must be rejected by LOV verification
    assert res["category_id"] is None
    assert res["classification_status"] == "unmatched"


def test_unknown_product_unmatched(classifier):
    res = classifier.classify_product(product_type="", part_desc="XYZABC 12345 Unrelated Nonexistent Product")
    assert res["category_id"] is None
    assert res["classification_status"] == "unmatched"
    assert res["classification_method"] == "unmatched"
    assert res["classification_confidence"] == 0.0


def test_missing_product_type(classifier):
    res = classifier.classify_product(product_type=None, part_desc="DCB518ASTS06G Diablo 1/2 in x 18 in Sanding Belt 6pc")
    assert res["category_id"] == "ABR_BELT_SANDING"
    assert res["classification_status"] == "classified"


def test_missing_description(classifier):
    res = classifier.classify_product(product_type="Sanding Belt", part_desc=None)
    assert res["category_id"] == "ABR_BELT_SANDING"
    assert res["classification_status"] == "classified"


def test_duplicate_product_classification_is_cached(classifier):
    res1 = classifier.classify_product(product_type="Sanding Belt", part_desc="Test Belt")
    res2 = classifier.classify_product(product_type="Sanding Belt", part_desc="Test Belt")
    assert res1 == res2
    assert "Sanding Belt|Test Belt|None|None" in classifier.classification_cache


def test_invalid_category_id_rejected(classifier):
    is_valid, rec = classifier.verify_lov("NON_EXISTENT_ID_999")
    assert is_valid is False
    assert rec is None


def test_invalid_parent_relationship_rejected(setup_taxonomy):
    bad_df = pd.DataFrame([{
        "category_id": "BAD_CAT",
        "category_name": "Bad Category",
        "parent_category_id": "NON_EXISTENT_PARENT_999",
        "parent_category_name": "Non Existent Parent",
        "hierarchy_level": 2,
        "category_path": "Non Existent Parent > Bad Category",
        "source_product_types": "Bad",
        "keywords": "bad",
        "aliases": "bad"
    }])
    with pytest.raises(AssertionError):
        setup_taxonomy.validate_taxonomy(bad_df)


def test_no_hallucinated_categories(classifier):
    res = classifier.classify_product(product_type="Cut-Off Disc", part_desc="Metal Cut-Off Disc")
    assert res["category_id"] in classifier.categories_by_id
    assert res["parent_category_id"] in classifier.categories_by_id
