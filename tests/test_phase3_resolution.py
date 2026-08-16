import pytest
from src.understanding.master_data import MasterDataLoader
from src.understanding.resolver import EntityResolver, normalize_name


@pytest.fixture
def resolver():
    loader = MasterDataLoader()
    return EntityResolver(master_loader=loader)


def test_normalize_name():
    assert normalize_name("Freud Inc (2435)") == "freud inc"
    assert normalize_name("FREUD INC.") == "freud inc"
    assert normalize_name(" Freud, Inc. ") == "freud inc"
    assert normalize_name("Jam Industrial Supply LLC (JAMIN)") == "jam industrial supply llc"
    assert normalize_name("3 M Co") == "3 m co"


def test_exact_manufacturer_match(resolver):
    res = resolver.resolve_manufacturer("Freud Inc")
    assert res["manufacturer_canonical"] == "Freud Inc"
    assert res["manufacturer_id"] == "2435"
    assert res["manufacturer_match_status"] == "matched"
    assert res["manufacturer_match_method"] == "exact"
    assert res["manufacturer_confidence"] == 1.0


def test_case_difference_match(resolver):
    res = resolver.resolve_manufacturer("freud inc")
    assert res["manufacturer_canonical"] == "Freud Inc"
    assert res["manufacturer_match_status"] == "matched"
    assert res["manufacturer_match_method"] in ["exact", "normalized"]


def test_punctuation_difference_match(resolver):
    res = resolver.resolve_manufacturer("Freud, Inc.")
    assert res["manufacturer_canonical"] == "Freud Inc"
    assert res["manufacturer_match_status"] == "matched"
    assert res["manufacturer_match_method"] == "normalized"


def test_parentheses_code_removal_match(resolver):
    res = resolver.resolve_manufacturer("Freud Inc (2435)")
    assert res["manufacturer_canonical"] == "Freud Inc"
    assert res["manufacturer_id"] == "2435"
    assert res["manufacturer_match_status"] == "matched"
    assert res["manufacturer_match_method"] == "normalized"


def test_fuzzy_typo_match(resolver):
    res = resolver.resolve_manufacturer("Freud Incc")
    assert res["manufacturer_canonical"] == "Freud Inc"
    assert res["manufacturer_match_status"] == "matched"
    assert res["manufacturer_match_method"] == "fuzzy"


def test_unmatched_manufacturer(resolver):
    res = resolver.resolve_manufacturer("NonExistent Unknown Manufacturer XYZ 999")
    assert res["manufacturer_canonical"] is None
    assert res["manufacturer_id"] is None
    assert res["manufacturer_match_status"] == "unmatched"
    assert res["manufacturer_match_method"] == "none"
    assert res["manufacturer_confidence"] == 0.0


def test_exact_brand_match(resolver):
    res = resolver.resolve_brand("Diablo", "Diablo")
    assert res["brand_canonical"] == "Diablo"
    assert res["brand_id"] == "BRD_DIABLO"
    assert res["brand_match_status"] == "matched"
    assert res["brand_match_method"] == "exact"


def test_manufacturer_brand_relationship(resolver):
    res_m = resolver.resolve_manufacturer("Freud Inc (2435)")
    res_b = resolver.resolve_brand(raw_brand=None, phase2_brand="Diablo", resolved_manufacturer=res_m["manufacturer_canonical"])

    assert res_m["manufacturer_canonical"] == "Freud Inc"
    assert res_b["brand_canonical"] == "Diablo"
    assert res_b["brand_match_status"] == "matched"

    # Test relationship validation helper directly
    is_valid = resolver.loader.validate_relationship("Freud Inc", "Diablo")
    assert is_valid is True


def test_no_hallucinated_manufacturer(resolver):
    res = resolver.resolve_manufacturer("Random Nonexistent Corp")
    if res["manufacturer_canonical"] is not None:
        assert res["manufacturer_canonical"] in resolver.loader.manufacturer_records


def test_no_hallucinated_brand(resolver):
    res = resolver.resolve_brand("NonExistent Brand 1234", "NonExistent Brand 1234")
    if res["brand_canonical"] is not None:
        assert res["brand_canonical"] in resolver.loader.brand_records
