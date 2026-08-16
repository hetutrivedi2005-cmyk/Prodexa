import os
import json
import pytest
import pandas as pd

from src.validation.validation_result import ValidationResult
from src.validation.character_limits import CharacterLimitValidator
from src.validation.quality_gate import ProductQualityGate
from src.validation.validation_engine import ValidationEngine
from src.validation.phase10_pipeline import get_file_hashes, verify_immutability


@pytest.fixture(scope="module")
def engine():
    return ValidationEngine()


@pytest.fixture(scope="module")
def quality_gate():
    return ProductQualityGate()


@pytest.fixture(scope="module")
def char_validator():
    return CharacterLimitValidator()


def test_1_validation_result_valid_instantiation():
    res = ValidationResult("V1", "P1", "brand", "REQ", "PASS", "INFO", "msg")
    assert res.validation_id == "V1"
    assert res.status == "PASS"


def test_2_validation_result_invalid_status_raises_error():
    with pytest.raises(ValueError):
        ValidationResult("V1", "P1", "brand", "REQ", "INVALID_STATUS", "INFO", "msg")


def test_3_validation_result_invalid_severity_raises_error():
    with pytest.raises(ValueError):
        ValidationResult("V1", "P1", "brand", "REQ", "PASS", "INVALID_SEVERITY", "msg")


def test_4_validation_result_to_dict():
    res = ValidationResult("V1", "P1", "brand", "REQ", "PASS", "INFO", "msg")
    d = res.to_dict()
    assert isinstance(d, dict)
    assert d["validation_id"] == "V1"


def test_5_character_limits_pass(char_validator):
    res = char_validator.validate_field("P1", "invoice_description", "Short text")
    assert res.status == "PASS"
    assert res.severity == "INFO"


def test_6_character_limits_fail(char_validator):
    res = char_validator.validate_field("P1", "invoice_description", "A" * 60)
    assert res.status == "FAIL"
    assert res.severity == "ERROR"


def test_7_quality_gate_pass(quality_gate):
    res = [ValidationResult("V1", "P1", "b", "r", "PASS", "INFO", "m")]
    st, err, warn = quality_gate.evaluate_quality_gate(res)
    assert st == "PASS" and err == 0 and warn == 0


def test_8_quality_gate_pass_with_warnings(quality_gate):
    res = [ValidationResult("V1", "P1", "b", "r", "WARNING", "WARNING", "m")]
    st, err, warn = quality_gate.evaluate_quality_gate(res)
    assert st == "PASS_WITH_WARNINGS" and err == 0 and warn == 1


def test_9_quality_gate_fail(quality_gate):
    res = [ValidationResult("V1", "P1", "b", "r", "FAIL", "ERROR", "m")]
    st, err, warn = quality_gate.evaluate_quality_gate(res)
    assert st == "FAIL" and err == 1


def test_10_required_fields_valid(engine):
    p = pd.Series({"brand": "3M", "part_manuf": "3M", "manufacturer_part_number": "775L", "category_id": "ABR", "product_type": "Disc"})
    res = engine.validate_required_fields(p)
    assert all(r.status == "PASS" for r in res)


def test_11_required_fields_missing_brand(engine):
    p = pd.Series({"brand": "", "part_manuf": "", "manufacturer_part_number": "775L", "category_id": "ABR", "product_type": "Disc"})
    res = engine.validate_required_fields(p)
    assert any(r.attribute_name == "brand" and r.status == "FAIL" for r in res)


def test_12_required_fields_missing_mpn(engine):
    p = pd.Series({"brand": "3M", "part_manuf": "3M", "manufacturer_part_number": "", "category_id": "ABR", "product_type": "Disc"})
    res = engine.validate_required_fields(p)
    assert any(r.attribute_name == "mpn" and r.status == "FAIL" for r in res)


def test_13_lov_compliance_pass(engine):
    res = engine.validate_lov_compliance("P1", "material", "PVC")
    assert res.status == "PASS"


def test_14_lov_compliance_fail(engine):
    res = engine.validate_lov_compliance("P1", "material", "Shiny Metal")
    assert res.status == "FAIL"


def test_15_lov_compliance_not_applicable(engine):
    res = engine.validate_lov_compliance("P1", "non_lov_attr", "Val")
    assert res.status == "NOT_APPLICABLE"


def test_16_uom_compliance_pass(engine):
    res = engine.validate_uom_compliance("P1", "dimensions", "24 in")
    assert res.status == "PASS"


def test_17_uom_compliance_fail(engine):
    res = engine.validate_uom_compliance("P1", "dimensions", "15 xyz")
    assert res.status == "FAIL"


def test_18_source_evidence_pass(engine):
    ev = {"source_id": "S1", "source_url": "http://m.com", "evidence_text": "Material: PVC", "evidence_id": "E1"}
    res = engine.validate_source_evidence("P1", "material", ev)
    assert res.status == "PASS"


def test_19_source_evidence_missing(engine):
    res = engine.validate_source_evidence("P1", "material", None)
    assert res.status in ["FAIL", "WARNING"]


def test_20_provenance_pass(engine):
    ev = {
        "attribute_name": "material", "value": "PVC", "source_id": "S1", "source_url": "http://m.com",
        "source_type": "mfg", "manufacturer": "Mfg", "normalized_mpn": "M1", "evidence_text": "text",
        "confidence": 0.95, "status": "verified"
    }
    res = engine.validate_provenance("P1", "material", ev)
    assert res.status == "PASS"


def test_21_provenance_incomplete(engine):
    ev = {"attribute_name": "material", "value": "PVC"}
    res = engine.validate_provenance("P1", "material", ev)
    assert res.status in ["FAIL", "WARNING"]


def test_22_identity_pass(engine):
    ev = {"product_id": "P1", "normalized_mpn": "MPN1", "mpn": "MPN1", "manufacturer": "3M", "attribute_name": "m"}
    res = engine.validate_identity("MPN1", "3M", ev)
    assert all(r.status == "PASS" for r in res)


def test_23_identity_mpn_fail(engine):
    ev = {"product_id": "P1", "normalized_mpn": "MPN_WRONG", "mpn": "MPN_WRONG", "manufacturer": "3M", "attribute_name": "m"}
    res = engine.validate_identity("MPN1", "3M", ev)
    assert any(r.attribute_name == "mpn" and r.status == "FAIL" for r in res)


def test_24_identity_mfg_fail(engine):
    ev = {"product_id": "P1", "normalized_mpn": "MPN1", "mpn": "MPN1", "manufacturer": "DEWALT", "attribute_name": "m"}
    res = engine.validate_identity("MPN1", "3M", ev)
    assert any(r.attribute_name == "manufacturer" and r.status == "FAIL" for r in res)


def test_25_category_attributes_pass(engine):
    res = engine.validate_category_attributes("P1", "CAT_UNCONSTRAINED", "material")
    assert res.status == "PASS"


def test_26_category_attributes_warning(engine):
    res = engine.validate_category_attributes("P1", "BLD_DECK_PVC", "color_temperature")
    assert res.status == "WARNING"


def test_27_conflicts_warning(engine):
    res = engine.validate_conflicts("P1", "conflict", True)
    assert res.status == "WARNING"


def test_28_data_types_pass(engine):
    res = engine.validate_data_types("P1", 0.95, "verified")
    assert all(r.status == "PASS" for r in res)


def test_29_data_types_confidence_fail(engine):
    res = engine.validate_data_types("P1", 1.5, "verified")
    assert any(r.attribute_name == "confidence" and r.status == "FAIL" for r in res)


def test_30_data_types_status_fail(engine):
    res = engine.validate_data_types("P1", 0.95, "INVALID_ENUM")
    assert any(r.attribute_name == "status" and r.status == "FAIL" for r in res)


def test_31_referential_integrity_pass(engine):
    ev = {"product_id": "P1", "evidence_id": "E1", "source_id": "S1", "source_url": "http://m.com"}
    res = engine.validate_referential_integrity("P1", ev)
    assert res.status == "PASS"


def test_32_referential_integrity_fail(engine):
    ev = {"product_id": "", "evidence_id": "E1", "source_id": "S1"}
    res = engine.validate_referential_integrity("P1", ev)
    assert res.status in ["FAIL", "WARNING"]


def test_33_immutability_verification():
    h = get_file_hashes()
    assert len(h) == 17
    verify_immutability(h)


def test_34_phase10_output_files_exist():
    assert os.path.exists("data/processed/validated_products.csv")
    assert os.path.exists("data/validation/validation_results.jsonl")
    assert os.path.exists("data/validation/validation_summary.json")
    assert os.path.exists("reports/phase10_validation_report.txt")
    assert os.path.exists("reports/phase10_adversarial_audit.txt")
    assert os.path.exists("reports/phase10_final_acceptance.txt")


def test_35_validated_products_column_preservation():
    df_p9 = pd.read_csv("data/processed/evidence_enriched_products.csv")
    df_p10 = pd.read_csv("data/processed/validated_products.csv")
    for col in df_p9.columns:
        assert col in df_p10.columns
    assert "validation_status" in df_p10.columns


def test_36_validation_summary_json_schema():
    with open("data/validation/validation_summary.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        assert "total_products" in d
        assert "products_passed" in d


def test_37_validation_results_jsonl_schema():
    with open("data/validation/validation_results.jsonl", "r", encoding="utf-8") as f:
        line = f.readline()
        assert line
        d = json.loads(line)
        assert "validation_id" in d
        assert "status" in d


def test_38_validation_report_metrics():
    with open("reports/phase10_validation_report.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "DATASET SUMMARY" in content
        assert "LOV compliance %:" in content


def test_39_adversarial_report_exists():
    with open("reports/phase10_adversarial_audit.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "Adversarial Audit:                  PASS" in content or "Cases passed:                       35" in content


def test_40_final_acceptance_report_exists():
    with open("reports/phase10_final_acceptance.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "Overall Phase 10 Status:            PASS" in content
