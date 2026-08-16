import pytest
import json
import pandas as pd
from unittest.mock import MagicMock
from src.understanding.lov_builder import LOVBuilder
from src.understanding.lov_engine import LOVResolver


@pytest.fixture(scope="module")
def setup_lov_masters():
    builder = LOVBuilder()
    df_lov, df_uom = builder.build_masters()
    builder.validate_masters(df_lov, df_uom)
    return builder


@pytest.fixture
def resolver(setup_lov_masters):
    return LOVResolver()


def test_1_exact_lov_match(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "grit", "P80")
    assert res["status"] == "resolved"
    assert res["method"] in ["exact", "normalized"]
    assert res["canonical_value"] == "P80"
    assert res["confidence"] >= 0.95


def test_2_case_normalization(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "grit", "p80")
    assert res["status"] == "resolved"
    assert res["canonical_value"] == "P80"


def test_3_whitespace_normalization(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "grit", "  P80  ")
    assert res["status"] == "resolved"
    assert res["canonical_value"] == "P80"


def test_4_alias_ss_to_stainless_steel(resolver):
    res = resolver.resolve_value("APP_CLEAN_LAUNDRY", "color_finish", "SS")
    assert res["status"] == "resolved"
    assert res["method"] == "alias"
    assert res["canonical_value"] == "Stainless Steel"


def test_5_alias_brs_to_brass(resolver):
    res = resolver.resolve_value("APP_CLEAN_LAUNDRY", "color_finish", "BRS")
    assert res["status"] == "resolved"
    assert res["method"] == "alias"
    assert res["canonical_value"] == "Brass"


def test_6_alias_al_to_aluminum(resolver):
    res = resolver.resolve_value("BLD_DECK_PVC", "material", "AL")
    assert res["status"] == "resolved"
    assert res["method"] == "alias"
    assert res["canonical_value"] == "Aluminum"


def test_7_inch_to_in_uom(resolver):
    res = resolver.resolve_value("ABR_DISC_GEN", "diameter", "5 INCH")
    assert res["status"] == "resolved"
    assert res["canonical_value"] == "5 in"


def test_8_mm_to_mm_uom(resolver):
    res = resolver.resolve_value("ABR_DISC_CUT", "arbor_size", "20 MM")
    assert res["status"] == "resolved"
    assert res["canonical_value"] in ["20mm", "20 mm"]


def test_9_20v_to_20v_uom(resolver):
    res = resolver.resolve_value("PWR_ACC_BATT", "voltage", "20V")
    assert res["status"] == "resolved"
    assert res["canonical_value"] == "20V"


def test_10_60w_to_60w_uom(resolver):
    res = resolver.resolve_value("LGT_BULB_LED", "wattage", "60W")
    assert res["status"] == "resolved"
    assert res["canonical_value"] == "60W"


def test_11_numeric_normalization(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "pack_quantity", "6.0")
    assert res["status"] == "resolved"
    assert res["canonical_value"] in ["6", "6.0"]


def test_12_type_aware_fuzzy_match_string(resolver):
    res = resolver.resolve_value("APP_CLEAN_LAUNDRY", "color_finish", "Stainles Steel")
    assert res["status"] == "resolved"
    assert res["method"] == "fuzzy"
    assert res["canonical_value"] == "Stainless Steel"


def test_13_type_aware_fuzzy_match_rejection_numeric(resolver):
    # Numeric values like "5" must NEVER fuzzy-match "50" or "5 in"
    res = resolver.resolve_value("ABR_DISC_CUT", "diameter", "5")
    assert res["canonical_value"] != "50"
    assert res["canonical_value"] != "50.0"


def test_14_ambiguous_candidate_rejection(resolver):
    res = resolver.resolve_value("BLD_DECK_PVC", "color", "Ambiguous Unclear Multi Color String")
    assert res["status"] in ["ambiguous", "unresolved", "resolved", "canonical"]


def test_15_invalid_lov_value_rejection(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "grit", "INVALID_GRIT_XYZ")
    assert res["status"] == "unresolved"
    assert res["canonical_value"] is None


def test_16_llm_valid_candidate_acceptance():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({"selected_value": "Stainless Steel", "confidence": 0.93})
    mock_client.models.generate_content.return_value = mock_resp

    llm_resolver = LOVResolver(client=mock_client)
    res = llm_resolver.resolve_value("APP_CLEAN_LAUNDRY", "color_finish", "S.Steel")
    assert res["status"] == "resolved"
    assert res["canonical_value"] == "Stainless Steel"


def test_17_llm_invented_value_rejection():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({"selected_value": "VIBRANT_GOLD_UNAPPROVED", "confidence": 0.99})
    mock_client.models.generate_content.return_value = mock_resp

    llm_resolver = LOVResolver(client=mock_client)
    res = llm_resolver.resolve_value("APP_CLEAN_LAUNDRY", "color_finish", "Unapproved Gold")
    assert res["status"] == "unresolved"
    assert res["canonical_value"] is None


def test_18_category_specific_lov_restriction(resolver):
    # Wattage is not defined for Sanding Belts
    res = resolver.resolve_value("ABR_BELT_SANDING", "wattage", "60W")
    assert res["status"] == "unresolved"


def test_19_unsupported_attribute_rejection(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "NON_EXISTENT_ATTRIBUTE", "Some Value")
    assert res["status"] == "unresolved"


def test_20_resolution_cache_deduplication(resolver):
    res1 = resolver.resolve_value("APP_CLEAN_LAUNDRY", "color_finish", "SS")
    res2 = resolver.resolve_value("APP_CLEAN_LAUNDRY", "color_finish", "SS")
    assert res1 == res2


def test_21_invalid_category_rejection(resolver):
    res = resolver.resolve_value("INVALID_CAT_ID", "grit", "P80")
    assert res["status"] == "unresolved"


def test_22_invalid_attribute_rejection(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "invalid_attr", "P80")
    assert res["status"] == "unresolved"


def test_23_confidence_bounds(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "grit", "P80")
    assert 0.0 <= res["confidence"] <= 1.0


def test_24_json_schema_validation(resolver):
    res = resolver.resolve_value("ABR_BELT_SANDING", "grit", "P80")
    assert "raw_value" in res
    assert "canonical_value" in res
    assert "method" in res
    assert "confidence" in res
    assert "status" in res


def test_25_phase5_column_preservation():
    df_p5 = pd.read_csv("data/processed/attributes_enriched_products.csv")
    assert len(df_p5) == 1000
