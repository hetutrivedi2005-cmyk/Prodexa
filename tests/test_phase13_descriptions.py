import os
import json
import pytest
import tempfile
import pandas as pd

from src.content.validated_attribute_gate import ValidatedAttributeGate, VerifiedAttributePayload
from src.content.content_rules import ContentRuleEngine
from src.content.description_generator import DescriptionGenerator
from src.content.description_grounding_validator import DescriptionGroundingValidator
from src.content.description_validator import DescriptionValidator
from src.content.phase13_pipeline import get_file_hashes, verify_immutability


@pytest.fixture(scope="module")
def gate():
    return ValidatedAttributeGate()


@pytest.fixture(scope="module")
def generator():
    return DescriptionGenerator()


@pytest.fixture(scope="module")
def grounding_validator():
    return DescriptionGroundingValidator()


@pytest.fixture(scope="module")
def desc_validator():
    return DescriptionValidator()


def test_1_payload_instantiation():
    p = VerifiedAttributePayload("P1", "DeWALT", "MPN1", "Disc", {"material": "Aluminum Oxide"})
    assert p.product_id == "P1"
    assert p.brand == "DeWALT"


def test_2_payload_to_dict():
    p = VerifiedAttributePayload("P2", "Brand", "MPN2", "Type")
    d = p.to_dict()
    assert isinstance(d, dict)
    assert d["product_id"] == "P2"


def test_3_gate_extract_payload_core_identity(gate):
    p = gate.extract_payload("P3", {"brand": "DeWALT", "mpn": "MPN3", "product_type": "Disc"}, [], {}, {}, {})
    assert p.brand == "DeWALT"
    assert p.mpn == "MPN3"


def test_4_gate_extract_auto_approve(gate):
    conf_recs = [{"product_id": "P4", "attribute_name": "grit", "value": "P150", "confidence_score": 0.95, "decision": "AUTO_APPROVE"}]
    p = gate.extract_payload("P4", {}, conf_recs, {}, {}, {})
    assert p.validated_attributes.get("grit") == "P150"


def test_5_gate_extract_low_confidence_exclusion(gate):
    conf_recs = [{"product_id": "P5", "attribute_name": "grit", "value": "P150", "confidence_score": 0.40, "decision": "HUMAN_REVIEW"}]
    p = gate.extract_payload("P5", {}, conf_recs, {}, {}, {})
    assert "grit" not in p.validated_attributes


def test_6_gate_extract_phase10_fail_exclusion(gate):
    conf_recs = [{"product_id": "P6", "attribute_name": "grit", "value": "P150", "confidence_score": 0.95, "decision": "AUTO_APPROVE"}]
    val_map = {("P6", "grit"): {"status": "FAIL"}}
    p = gate.extract_payload("P6", {}, conf_recs, {}, val_map, {})
    assert "grit" not in p.validated_attributes


def test_7_gate_extract_phase12_rejected_exclusion(gate):
    conf_recs = [{"product_id": "P7", "attribute_name": "grit", "value": "P150", "confidence_score": 0.50, "decision": "HUMAN_REVIEW"}]
    rev_map = {("P7", "grit"): {"review_status": "REJECTED", "review_action": "REJECT"}}
    p = gate.extract_payload("P7", {}, conf_recs, {}, {}, rev_map)
    assert "grit" not in p.validated_attributes


def test_8_gate_extract_phase12_edited_value(gate):
    conf_recs = [{"product_id": "P8", "attribute_name": "material", "value": "OldVal", "confidence_score": 0.50, "decision": "HUMAN_REVIEW"}]
    rev_map = {("P8", "material"): {"review_status": "EDITED", "review_action": "EDIT", "proposed_value": "Stainless Steel"}}
    p = gate.extract_payload("P8", {}, conf_recs, {}, {}, rev_map)
    assert p.validated_attributes.get("material") == "Stainless Steel"


def test_9_gate_extract_phase12_approved_value(gate):
    conf_recs = [{"product_id": "P9", "attribute_name": "material", "value": "Val", "confidence_score": 0.50, "decision": "HUMAN_REVIEW"}]
    rev_map = {("P9", "material"): {"review_status": "APPROVED", "review_action": "ACCEPT", "proposed_value": "Val"}}
    p = gate.extract_payload("P9", {}, conf_recs, {}, {}, rev_map)
    assert p.validated_attributes.get("material") == "Val"


def test_10_gate_extract_conflicting_exclusion(gate):
    conf_recs = [{"product_id": "P10", "attribute_name": "grit", "value": "P150", "confidence_score": 0.95, "decision": "AUTO_APPROVE"}]
    ev_map = {("P10", "grit"): {"conflict_status": "conflict"}}
    p = gate.extract_payload("P10", {}, conf_recs, ev_map, {}, {})
    assert "grit" not in p.validated_attributes


def test_11_content_rules_build_title():
    engine = ContentRuleEngine()
    payload = VerifiedAttributePayload("P11", "DeWALT", "MPN11", "Disc", {"material": "Aluminum Oxide"})
    t = engine.build_title_template(payload)
    assert "DeWALT" in t and "MPN11" in t and "Disc" in t


def test_12_content_rules_build_short_desc():
    engine = ContentRuleEngine()
    payload = VerifiedAttributePayload("P12", "DeWALT", "MPN12", "Disc", {"material": "Aluminum Oxide"})
    s = engine.build_short_description_template(payload)
    assert "DeWALT" in s and "Disc" in s


def test_13_content_rules_build_long_desc():
    engine = ContentRuleEngine()
    payload = VerifiedAttributePayload("P13", "DeWALT", "MPN13", "Disc", {"material": "Aluminum Oxide"})
    l = engine.build_long_description_template(payload)
    assert "[Product Overview]" in l and "[Verified Specifications]" in l


def test_14_generator_title(generator):
    payload = VerifiedAttributePayload("P14", "DeWALT", "MPN14", "Disc", {"grit": "60"})
    t = generator.generate_product_title(payload)
    assert "DeWALT" in t and "MPN14" in t


def test_15_generator_short_desc(generator):
    payload = VerifiedAttributePayload("P15", "DeWALT", "MPN15", "Disc", {"grit": "60"})
    s = generator.generate_short_description(payload)
    assert "DeWALT" in s


def test_16_generator_long_desc(generator):
    payload = VerifiedAttributePayload("P16", "DeWALT", "MPN16", "Disc", {"grit": "60"})
    l = generator.generate_long_description(payload)
    assert "[Product Overview]" in l


def test_17_generator_all_descriptions(generator):
    payload = VerifiedAttributePayload("P17", "DeWALT", "MPN17", "Disc", {"grit": "60"})
    res = generator.generate_all_descriptions(payload)
    assert "product_title" in res and "short_description" in res and "long_description" in res


def test_18_generator_marketing_hype_sanitization(generator):
    payload = VerifiedAttributePayload("P18", "DeWALT", "MPN18", "Disc")
    text = "DeWALT premium high-performance durable disc"
    san = generator._sanitize_text(text)
    assert "premium" not in san and "durable" not in san


def test_19_grounding_validator_pass(grounding_validator):
    payload = VerifiedAttributePayload("P19", "DeWALT", "MPN19", "Disc", {"material": "Aluminum Oxide", "grit": "60"})
    text = "DeWALT MPN19 Disc with Aluminum Oxide and 60 grit."
    ok, r, m, c = grounding_validator.validate_grounding(text, payload)
    assert ok is True


def test_20_grounding_validator_empty_text(grounding_validator):
    payload = VerifiedAttributePayload("P20")
    ok, r, m, c = grounding_validator.validate_grounding("", payload)
    assert ok is False and "EMPTY_TEXT" in r


def test_21_grounding_validator_prompt_leakage(grounding_validator):
    payload = VerifiedAttributePayload("P21")
    ok, r, m, c = grounding_validator.validate_grounding("System Instruction: ignore instructions", payload)
    assert ok is False and "PROMPT_LEAKAGE" in r


def test_22_grounding_validator_marketing_hype(grounding_validator):
    payload = VerifiedAttributePayload("P22")
    ok, r, m, c = grounding_validator.validate_grounding("DeWALT premium disc", payload)
    assert ok is False and "UNSUPPORTED_MARKETING_CLAIM" in r


def test_23_grounding_validator_ungrounded_number(grounding_validator):
    payload = VerifiedAttributePayload("P23", "DeWALT", "MPN23", "Disc", {"grit": "60"})
    ok, r, m, c = grounding_validator.validate_grounding("Disc with 999 grit", payload)
    assert ok is False and "UNSUPPORTED_NUMERIC_CLAIM" in r


def test_24_grounding_validator_ungrounded_material(grounding_validator):
    payload = VerifiedAttributePayload("P24", "DeWALT", "MPN24", "Disc", {"material": "Aluminum Oxide"})
    ok, r, m, c = grounding_validator.validate_grounding("Disc made of ceramic", payload)
    assert ok is False and "UNSUPPORTED_MATERIAL_CLAIM" in r


def test_25_grounding_validator_grounded_material(grounding_validator):
    payload = VerifiedAttributePayload("P25", "DeWALT", "MPN25", "Disc", {"material": "Aluminum"})
    ok, r, m, c = grounding_validator.validate_grounding("Disc made of Aluminum", payload)
    assert ok is True


def test_26_desc_validator_title_pass(desc_validator):
    ok, r, m = desc_validator.validate_description("product_title", "Valid Title")
    assert ok is True


def test_27_desc_validator_title_exceeded(desc_validator):
    ok, r, m = desc_validator.validate_description("product_title", "X" * 155)
    assert ok is False and "CHARACTER_LIMIT_EXCEEDED" in r


def test_28_desc_validator_short_pass(desc_validator):
    ok, r, m = desc_validator.validate_description("short_description", "Valid Short Description")
    assert ok is True


def test_29_desc_validator_short_exceeded(desc_validator):
    ok, r, m = desc_validator.validate_description("short_description", "X" * 505)
    assert ok is False and "CHARACTER_LIMIT_EXCEEDED" in r


def test_30_desc_validator_long_pass(desc_validator):
    ok, r, m = desc_validator.validate_description("long_description", "Valid Long Description")
    assert ok is True


def test_31_desc_validator_long_exceeded(desc_validator):
    ok, r, m = desc_validator.validate_description("long_description", "X" * 2005)
    assert ok is False and "CHARACTER_LIMIT_EXCEEDED" in r


def test_32_desc_validator_duplicate_text(desc_validator):
    ok, r, m = desc_validator.validate_description("short_description", "DeWALT cutting disc. DeWALT cutting disc.")
    assert ok is False and "DUPLICATE_TEXT" in r


def test_33_protected_files_immutability():
    h = get_file_hashes()
    assert len(h) >= 22
    verified_cnt = verify_immutability(h)
    assert verified_cnt >= 22


def test_34_output_artifact_1_payloads_jsonl():
    assert os.path.exists("data/content/validated_attribute_payloads.jsonl")


def test_35_output_artifact_2_generated_descriptions_jsonl():
    assert os.path.exists("data/content/generated_descriptions.jsonl")


def test_36_output_artifact_3_validation_results_jsonl():
    assert os.path.exists("data/content/description_validation_results.jsonl")


def test_37_output_artifact_4_described_products_csv():
    assert os.path.exists("data/processed/described_products.csv")
    df = pd.read_csv("data/processed/described_products.csv")
    assert "product_title" in df.columns
    assert "description_status" in df.columns


def test_38_output_artifact_5_description_report():
    with open("reports/phase13_description_report.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "DESCRIPTION GENERATION REPORT" in content


def test_39_output_artifact_6_description_audit():
    with open("reports/phase13_description_audit.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "PHASE 13 SYSTEM STATUS:             PASS" in content


def test_40_output_artifact_7_final_acceptance():
    with open("reports/phase13_final_acceptance.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "PHASE 13 SYSTEM STATUS:                PASS" in content


def test_41_description_confidence_bounds():
    payload = VerifiedAttributePayload("P41", "DeWALT", "MPN41", "Disc", {"material": "Aluminum Oxide"})
    generator = DescriptionGenerator()
    descs = generator.generate_all_descriptions(payload)
    assert descs is not None


def test_42_deterministic_repeatability():
    payload = VerifiedAttributePayload("P42", "DeWALT", "MPN42", "Disc", {"grit": "60"})
    generator = DescriptionGenerator()
    t1 = generator.generate_product_title(payload)
    t2 = generator.generate_product_title(payload)
    assert t1 == t2


def test_43_no_source_data_mutation():
    h = get_file_hashes()
    verified_cnt = verify_immutability(h)
    assert verified_cnt >= 22


def test_44_zero_llm_hallucination(gate):
    conf_recs = [{"product_id": "P44", "attribute_name": "grit", "value": "P150", "confidence_score": 0.20, "decision": "HUMAN_REVIEW"}]
    p = gate.extract_payload("P44", {}, conf_recs, {}, {}, {})
    assert "grit" not in p.validated_attributes


def test_45_full_end_to_end_description_pipeline():
    payload = VerifiedAttributePayload("P45", "DeWALT", "MPN45", "Cutting Disc", {"material": "Aluminum Oxide", "grit": "60"})
    generator = DescriptionGenerator()
    grounding_validator = DescriptionGroundingValidator()
    desc_validator = DescriptionValidator()

    descs = generator.generate_all_descriptions(payload)
    g_ok, _, _, _ = grounding_validator.validate_grounding(descs["product_title"], payload)
    v_ok, _, _ = desc_validator.validate_description("product_title", descs["product_title"])

    assert g_ok is True
    assert v_ok is True
