import os
import pytest
import pandas as pd
import json
from src.output.final_output_gate import FinalOutputGate
from src.output.product_schema import ProductFinalSchema, ProductIdentityModel, ProductDescriptionsModel, ProductValidationModel, EvidenceReferenceModel
from src.output.phase14_pipeline import run_phase14_pipeline


@pytest.fixture
def gate():
    return FinalOutputGate()


def test_1_identity_model():
    p = ProductIdentityModel(product_id="PROD-0001", mpn="MPN1", brand="Brand1", manufacturer="Man1", product_type="Type1")
    assert p.product_id == "PROD-0001"
    assert p.mpn == "MPN1"


def test_2_identity_model_optional():
    p = ProductIdentityModel(product_id="PROD-0002")
    assert p.brand is None


def test_3_descriptions_model():
    d = ProductDescriptionsModel(title="Title", short_description="Short", long_description="Long")
    assert d.title == "Title"


def test_4_descriptions_model_optional():
    d = ProductDescriptionsModel()
    assert d.title is None


def test_5_validation_model():
    v = ProductValidationModel(status="approved", confidence=0.96, description_status="validated")
    assert v.status == "approved"
    assert v.confidence == 0.96


def test_6_evidence_ref_model():
    e = EvidenceReferenceModel(product_id="PROD-0006", attribute="grit", value="P120", source_id="SRC-1")
    assert e.attribute == "grit"
    assert e.source_id == "SRC-1"


def test_7_final_schema_validation():
    p_id = ProductIdentityModel(product_id="PROD-0007")
    p_desc = ProductDescriptionsModel(title="Title")
    p_val = ProductValidationModel(status="approved", confidence=0.96)
    schema = ProductFinalSchema(product=p_id, attributes={"size": "1/2 in"}, descriptions=p_desc, validation=p_val)
    assert schema.product.product_id == "PROD-0007"
    assert schema.attributes["size"] == "1/2 in"


def test_8_gate_product_eligible(gate):
    p = {"validation_status": "PASS", "identity_valid": True}
    eligible, reason = gate.evaluate_product_eligibility("P8", p, {"validation_status": "PASS"})
    assert eligible is True
    assert reason is None


def test_9_gate_product_identity_fail(gate):
    p = {"validation_status": "FAIL", "identity_valid": False}
    eligible, reason = gate.evaluate_product_eligibility("P9", p, {"validation_status": "PASS"})
    assert eligible is False
    assert reason == "IDENTITY_MISMATCH"


def test_10_gate_product_description_fail(gate):
    p = {"validation_status": "PASS", "identity_valid": True}
    eligible, reason = gate.evaluate_product_eligibility("P10", p, {"validation_status": "FAIL"})
    assert eligible is False
    assert reason == "DESCRIPTION_VALIDATION_FAILED"


def test_11_gate_product_missing_description(gate):
    p = {"validation_status": "PASS", "identity_valid": True}
    eligible, reason = gate.evaluate_product_eligibility("P11", p, None)
    assert eligible is False
    assert reason == "DESCRIPTION_VALIDATION_FAILED"


def test_12_gate_attr_val_pass(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P12", "size", "1/2 in", None, None, {"status": "PASS"}, None)
    assert eligible is True


def test_13_gate_attr_val_fail(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P13", "size", "1/2 in", None, None, {"status": "FAIL"}, None)
    assert eligible is False
    assert reason == "VALIDATION_FAILED"


def test_14_gate_attr_conflict(gate):
    ev = {"conflict_status": "conflict"}
    eligible, reason = gate.evaluate_attribute_eligibility("P14", "size", "1/2 in", None, ev, None, None)
    assert eligible is False
    assert reason == "CONFLICT_DETECTED"


def test_15_gate_attr_rejected_in_review(gate):
    rev = {"review_status": "REJECTED", "review_action": "REJECT"}
    eligible, reason = gate.evaluate_attribute_eligibility("P15", "size", "1/2 in", None, None, None, rev)
    assert eligible is False
    assert reason == "ATTRIBUTE_REJECTED"


def test_16_gate_attr_pending_in_review(gate):
    rev = {"review_status": "PENDING"}
    eligible, reason = gate.evaluate_attribute_eligibility("P16", "size", "1/2 in", None, None, None, rev)
    assert eligible is False
    assert reason == "HUMAN_REVIEW_PENDING"


def test_17_gate_attr_escalated_in_review(gate):
    rev = {"review_status": "ESCALATED"}
    eligible, reason = gate.evaluate_attribute_eligibility("P17", "size", "1/2 in", None, None, None, rev)
    assert eligible is False
    assert reason == "HUMAN_REVIEW_PENDING"


def test_18_gate_attr_approved_in_review(gate):
    rev = {"review_status": "APPROVED", "review_action": "ACCEPT"}
    eligible, reason = gate.evaluate_attribute_eligibility("P18", "size", "1/2 in", None, None, None, rev)
    assert eligible is True


def test_19_gate_attr_edited_in_review(gate):
    rev = {"review_status": "EDITED", "review_action": "EDIT", "proposed_value": "EditedVal"}
    eligible, reason = gate.evaluate_attribute_eligibility("P19", "size", "1/2 in", None, None, None, rev)
    assert eligible is True


def test_20_gate_attr_missing_evidence_required(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P20", "material", "Steel", None, None, None, None)
    assert eligible is False
    assert reason == "EVIDENCE_REQUIRED_MISSING"


def test_21_gate_attr_missing_evidence_not_required(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P21", "size", "1/2 in", None, None, None, None)
    assert eligible is True


def test_22_gate_attr_ungrounded_evidence(gate):
    ev = {"verification_status": "unverified", "confidence": 0.95}
    eligible, reason = gate.evaluate_attribute_eligibility("P22", "material", "Steel", None, ev, None, None)
    assert eligible is False
    assert reason == "UNGROUNDED_EVIDENCE"


def test_23_gate_attr_low_confidence_evidence(gate):
    ev = {"verification_status": "verified", "confidence": 0.50}
    eligible, reason = gate.evaluate_attribute_eligibility("P23", "material", "Steel", None, ev, None, None)
    assert eligible is False
    assert reason == "UNGROUNDED_EVIDENCE"


def test_24_gate_attr_rejected_in_confidence(gate):
    c = {"decision": "REJECTED"}
    eligible, reason = gate.evaluate_attribute_eligibility("P24", "size", "1/2 in", c, None, None, None)
    assert eligible is False
    assert reason == "ATTRIBUTE_REJECTED"


def test_25_gate_attr_human_review_in_confidence(gate):
    c = {"decision": "HUMAN_REVIEW"}
    eligible, reason = gate.evaluate_attribute_eligibility("P25", "size", "1/2 in", c, None, None, None)
    assert eligible is False
    assert reason == "HUMAN_REVIEW_PENDING"


def test_26_gate_attr_brand_baseline(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P26", "brand", "Diablo", None, None, None, None)
    assert eligible is True


def test_27_gate_attr_mpn_baseline(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P27", "mpn", "DCB-1", None, None, None, None)
    assert eligible is True


def test_28_gate_attr_manufacturer_baseline(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P28", "manufacturer", "Freud", None, None, None, None)
    assert eligible is True


def test_29_gate_attr_product_type_baseline(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P29", "product_type", "Sanding Belt", None, None, None, None)
    assert eligible is True


def test_30_gate_attr_quantity_baseline(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P30", "quantity", "6", None, None, None, None)
    assert eligible is True


def test_31_gate_attr_dimensions_baseline(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P31", "dimensions", "24 in", None, None, None, None)
    assert eligible is True


def test_32_gate_attr_pack_quantity_baseline(gate):
    eligible, reason = gate.evaluate_attribute_eligibility("P32", "pack_quantity", "1", None, None, None, None)
    assert eligible is True


def test_33_schema_compliance_serialization():
    p_id = ProductIdentityModel(product_id="P33")
    p_desc = ProductDescriptionsModel(title="Title")
    p_val = ProductValidationModel(status="approved", confidence=0.96)
    schema = ProductFinalSchema(product=p_id, attributes={}, descriptions=p_desc, validation=p_val)
    dumped = schema.model_dump()
    assert dumped["product"]["product_id"] == "P33"


def test_34_schema_to_json_str():
    p_id = ProductIdentityModel(product_id="P34")
    p_desc = ProductDescriptionsModel(title="Title")
    p_val = ProductValidationModel(status="approved", confidence=0.96)
    schema = ProductFinalSchema(product=p_id, attributes={}, descriptions=p_desc, validation=p_val)
    json_str = schema.model_dump_json()
    assert '"product_id":"P34"' in json_str


def test_35_evidence_linkage_to_dict():
    ref = EvidenceReferenceModel(product_id="P35", attribute="grit", value="P120", source_id="SRC-1")
    assert ref.model_dump()["source_id"] == "SRC-1"


def test_36_final_product_json_exists():
    path = "data/final/product.json"
    assert os.path.exists(path)


def test_37_final_enriched_csv_exists():
    path = "data/final/enriched.csv"
    assert os.path.exists(path)


def test_38_final_validation_report_exists():
    path = "data/final/validation_report.csv"
    assert os.path.exists(path)


def test_39_final_evidence_json_exists():
    path = "data/final/evidence.json"
    assert os.path.exists(path)


def test_40_final_acceptance_report_exists():
    path = "reports/phase14_final_acceptance.txt"
    assert os.path.exists(path)


def test_41_final_output_report_exists():
    path = "reports/phase14_output_report.txt"
    assert os.path.exists(path)


def test_42_final_output_audit_exists():
    path = "reports/phase14_output_audit.txt"
    assert os.path.exists(path)


def test_43_enriched_csv_rows():
    df = pd.read_csv("data/final/enriched.csv")
    assert len(df) > 0
    assert "product_id" in df.columns


def test_44_validation_report_rows():
    df = pd.read_csv("data/final/validation_report.csv")
    assert len(df) > 0
    assert "exclusion_reason" in df.columns


def test_45_evidence_json_records():
    with open("data/final/evidence.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
