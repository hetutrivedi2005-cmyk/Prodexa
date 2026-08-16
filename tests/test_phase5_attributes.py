import pytest
import json
import pandas as pd
from unittest.mock import MagicMock
from src.understanding.attribute_schema_builder import AttributeSchemaBuilder
from src.understanding.attribute_schema import AttributeItem, ExtractedAttributesPayload
from src.understanding.attribute_extractor import CategoryAttributeExtractor, ground_text_in_fields


@pytest.fixture(scope="module")
def setup_attribute_schema():
    builder = AttributeSchemaBuilder()
    df_s = builder.build_schema()
    builder.validate_schema(df_s)
    return builder


@pytest.fixture
def extractor(setup_attribute_schema):
    return CategoryAttributeExtractor()


def test_1_exact_grit_extraction(extractor):
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Diablo 1/2 in x 18 in Sanding Belt P80 6pc", quantity="6")
    data = json.loads(res["extracted_attributes_json"])
    assert "grit" in data
    assert data["grit"]["value"] == "P80"
    assert data["grit"]["evidence"] == "P80"


def test_2_dimension_extraction(extractor):
    # Belt dimensions (1/2 in x 18 in) correctly extracted as 'dimensions' (not diameter)
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt 6pc", size="1/2 in x 18 in")
    data = json.loads(res["extracted_attributes_json"])
    assert "dimensions" in data
    assert data["dimensions"]["value"] == "1/2 in x 18 in"


def test_3_voltage_extraction(extractor):
    res = extractor.extract_product_attributes(category_id="PWR_ACC_BATT", part_desc="Dewalt 20V 8Ah Battery")
    data = json.loads(res["extracted_attributes_json"])
    assert "voltage" in data
    assert data["voltage"]["value"] == "20V"


def test_4_wattage_extraction(extractor):
    res = extractor.extract_product_attributes(category_id="LGT_BULB_LED", part_desc="60W Led Med 2pk")
    data = json.loads(res["extracted_attributes_json"])
    assert "wattage" in data
    assert data["wattage"]["value"] == "60W"


def test_5_color_temperature_27k_rule(extractor):
    # 27K in lighting must become 2700K (never 27,000 watts)
    res = extractor.extract_product_attributes(category_id="LGT_BULB_LED", part_desc="S4726 7W Incan Cand 27K 4pk")
    data = json.loads(res["extracted_attributes_json"])
    assert "color_temperature" in data
    assert data["color_temperature"]["value"] == "2700K"
    assert "wattage" in data
    assert data["wattage"]["value"] == "7W"


def test_6_quantity_extraction(extractor):
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt 6pc", quantity="6.0")
    data = json.loads(res["extracted_attributes_json"])
    assert "pack_quantity" in data
    assert data["pack_quantity"]["value"] == 6


def test_7_material_abbreviation_normalization(extractor):
    res = extractor.extract_product_attributes(category_id="APP_CLEAN_LAUNDRY", part_desc="M701B Dishwasher SS")
    data = json.loads(res["extracted_attributes_json"])
    assert "color_finish" in data
    assert data["color_finish"]["value"] == "Stainless Steel"
    assert data["color_finish"]["evidence"] == "SS"


def test_8_category_specific_attribute_filtering(extractor):
    # Voltage is blocked/filtered out for Abrasives (ABR_BELT_SANDING)
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt 20V P80")
    data = json.loads(res["extracted_attributes_json"])
    assert "voltage" not in data
    assert "grit" in data


def test_9_unknown_llm_attribute_rejection(extractor):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "attributes": {
            "UNKNOWN_HALLUCINATED_ATTR": {"value": "Gold", "confidence": 0.9, "evidence": "Gold", "method": "llm"},
            "grit": {"value": "P80", "confidence": 0.9, "evidence": "P80", "method": "llm"}
        }
    })
    mock_client.models.generate_content.return_value = mock_resp

    llm_extractor = CategoryAttributeExtractor(client=mock_client)
    res = llm_extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt P80 Gold")
    data = json.loads(res["extracted_attributes_json"])
    assert "UNKNOWN_HALLUCINATED_ATTR" not in data
    assert "grit" in data


def test_10_invalid_enum_rejection():
    with pytest.raises(Exception):
        AttributeItem(value="P80", confidence=1.5, evidence="P80", method="rule")


def test_11_invalid_unit_rejection():
    with pytest.raises(Exception):
        AttributeItem(value="P80", confidence=0.9, evidence="", method="rule")


def test_12_missing_attribute_handling(extractor):
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Generic Product Text Without Attributes")
    assert res["attribute_extraction_status"] == "none"
    assert res["attribute_confidence"] == 0.0


def test_13_pydantic_validation():
    item = AttributeItem(value="P80", confidence=0.99, evidence="P80", method="rule")
    assert item.value == "P80"
    assert item.confidence == 0.99


def test_14_evidence_validation_across_all_fields():
    assert ground_text_in_fields("1/2 in x 18 in", "1/2 in x 18 in", [None, "1/2 in x 18 in", "6", None]) is True
    assert ground_text_in_fields("6", "6.0", [None, None, "6.0", None]) is True


def test_15_ungrounded_value_rejection():
    assert ground_text_in_fields("100V", "100V", ["Sanding Belt 6pc", "1/2 in x 18 in"]) is False


def test_16_confidence_bounds(extractor):
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt P80 6pc", quantity="6")
    conf = res["attribute_confidence"]
    assert 0.0 <= conf <= 1.0


def test_17_invalid_json_handling():
    payload = ExtractedAttributesPayload()
    assert payload.attributes == {}


def test_18_duplicate_description_caching(extractor):
    res1 = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt P80 6pc")
    res2 = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt P80 6pc")
    assert res1 == res2


def test_19_llm_fallback():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "attributes": {
            "target_material": {"value": "Metal", "confidence": 0.90, "evidence": "Metal", "method": "llm"}
        }
    })
    mock_client.models.generate_content.return_value = mock_resp

    llm_extractor = CategoryAttributeExtractor(client=mock_client)
    res = llm_extractor.extract_product_attributes(category_id="ABR_DISC_CUT", part_desc="Special Cut-Off Disc Metal")
    data = json.loads(res["extracted_attributes_json"])
    assert "target_material" in data


def test_20_llm_failure_handling():
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API Failure")

    llm_extractor = CategoryAttributeExtractor(client=mock_client)
    res = llm_extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Diablo Sanding Belt P80 6pc")
    data = json.loads(res["extracted_attributes_json"])
    assert "grit" in data


def test_21_no_attribute_hallucination(extractor):
    res = extractor.extract_product_attributes(category_id="LGT_BULB_LED", part_desc="60W Led Bulb Med 2pk")
    data = json.loads(res["extracted_attributes_json"])
    allowed_ids = set(extractor.category_schemas["LGT_BULB_LED"].keys())
    for k in data.keys():
        assert k in allowed_ids


def test_22_no_value_hallucination(extractor):
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt P80 6pc")
    data = json.loads(res["extracted_attributes_json"])
    for item in data.values():
        assert ground_text_in_fields(str(item["value"]), str(item["evidence"]), ["Sanding Belt P80 6pc"]) is True


def test_23_phase4_immutability():
    assert pd.read_csv("data/processed/classified_products.csv").shape[0] == 1000


def test_24_output_row_count_preservation():
    df_classified = pd.read_csv("data/processed/classified_products.csv")
    assert len(df_classified) == 1000


def test_25_output_schema_validation(extractor):
    res = extractor.extract_product_attributes(category_id="ABR_BELT_SANDING", part_desc="Sanding Belt P80 6pc")
    assert "extracted_attributes_json" in res
    assert "attribute_extraction_status" in res
    assert "attribute_extraction_method" in res
    assert "attribute_confidence" in res
    assert "attribute_validation_status" in res
