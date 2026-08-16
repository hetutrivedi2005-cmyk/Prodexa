import os
import json
import pytest
import pandas as pd

from src.confidence.confidence_model import AttributeConfidence
from src.confidence.confidence_rules import ConfidenceRulesEngine, SOURCE_AUTHORITY_SCORES
from src.confidence.confidence_engine import ConfidenceEngine
from src.confidence.confidence_explainer import ConfidenceExplainer
from src.confidence.confidence_registry import ConfidenceRegistry
from src.confidence.phase11_pipeline import get_file_hashes, verify_immutability


@pytest.fixture(scope="module")
def rules_engine():
    return ConfidenceRulesEngine()


@pytest.fixture(scope="module")
def confidence_engine():
    return ConfidenceEngine()


@pytest.fixture(scope="module")
def explainer():
    return ConfidenceExplainer()


def test_1_attribute_confidence_valid_instantiation():
    conf = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE")
    assert conf.product_id == "P1"
    assert conf.confidence_score == 0.95
    assert conf.decision == "AUTO_APPROVE"


def test_2_attribute_confidence_out_of_bounds_raises_error():
    with pytest.raises(ValueError):
        AttributeConfidence("P1", "material", "Aluminum Oxide", 1.5, 150, "AUTO_APPROVE")


def test_3_attribute_confidence_invalid_decision_raises_error():
    with pytest.raises(ValueError):
        AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "INVALID_DECISION")


def test_4_attribute_confidence_to_dict():
    conf = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE")
    d = conf.to_dict()
    assert isinstance(d, dict)
    assert d["confidence_score"] == 0.95
    assert d["decision"] == "AUTO_APPROVE"


def test_5_rules_source_authority_official_mfg(rules_engine):
    score, _, _, sigs, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", {"evidence_text": "txt", "status": "verified"}, {"status": "PASS"}, True, False)
    assert sigs["source_authority"] == 1.00


def test_6_rules_source_authority_distributor(rules_engine):
    score, _, _, sigs, _ = rules_engine.calculate_confidence("authorized_distributor_technical_page", {"evidence_text": "txt", "status": "verified"}, {"status": "PASS"}, True, False)
    assert sigs["source_authority"] == 0.60


def test_7_rules_source_authority_marketplace(rules_engine):
    score, _, _, sigs, _ = rules_engine.calculate_confidence("marketplace", {"evidence_text": "txt", "status": "verified"}, {"status": "PASS"}, True, False)
    assert sigs["source_authority"] == 0.00


def test_8_rules_evidence_grounding_complete(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified", "mpn_verified": True, "manufacturer_verified": True}
    _, _, _, sigs, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "PASS"}, True, False)
    assert sigs["evidence_grounding"] == 1.00


def test_9_rules_evidence_grounding_missing(rules_engine):
    _, _, _, sigs, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", None, {"status": "PASS"}, True, False)
    assert sigs["evidence_grounding"] == 0.00


def test_10_rules_lov_compliance_valid_vs_invalid(rules_engine):
    ev_valid = {"evidence_text": "txt", "status": "verified", "lov_valid": True}
    ev_invalid = {"evidence_text": "txt", "status": "verified", "lov_valid": False}
    _, _, _, sigs_v, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev_valid, {"status": "PASS"}, True, False)
    _, _, _, sigs_inv, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev_invalid, {"status": "PASS"}, True, False)
    assert sigs_v["lov_compliance"] == 1.00
    assert sigs_inv["lov_compliance"] == 0.00


def test_11_rules_uom_compliance_valid_vs_invalid(rules_engine):
    ev_valid = {"evidence_text": "txt", "status": "verified", "uom_valid": True}
    ev_invalid = {"evidence_text": "txt", "status": "verified", "uom_valid": False}
    _, _, _, sigs_v, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev_valid, {"status": "PASS"}, False, True)
    _, _, _, sigs_inv, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev_invalid, {"status": "PASS"}, False, True)
    assert sigs_v["uom_compliance"] == 1.00
    assert sigs_inv["uom_compliance"] == 0.00


def test_12_rules_validation_score_pass_vs_fail(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified"}
    _, _, _, sigs_p, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "PASS"}, True, False)
    _, _, _, sigs_f, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "FAIL"}, True, False)
    assert sigs_p["validation_score"] == 1.00
    assert sigs_f["validation_score"] == 0.00


def test_13_dynamic_weight_renormalization_na_uom(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified"}
    _, _, _, sigs, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "PASS"}, True, False)
    assert sigs["uom_compliance"] is None


def test_14_dynamic_weight_renormalization_na_lov(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified"}
    _, _, _, sigs, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "PASS"}, False, False)
    assert sigs["lov_compliance"] is None


def test_15_threshold_auto_approve(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified", "mpn_verified": True, "manufacturer_verified": True}
    score, _, dec, _, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "PASS"}, True, False)
    assert score >= 0.90
    assert dec == "AUTO_APPROVE"


def test_16_threshold_review_recommended(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified", "confidence": 0.8}
    score, _, dec, _, _ = rules_engine.calculate_confidence("authorized_distributor_technical_page", ev, {"status": "PASS"}, True, False)
    assert dec in ["REVIEW_RECOMMENDED", "HUMAN_REVIEW"]


def test_17_threshold_human_review(rules_engine):
    score, _, dec, _, _ = rules_engine.calculate_confidence("marketplace", None, {"status": "FAIL"}, True, False)
    assert score < 0.70
    assert dec == "HUMAN_REVIEW"


def test_18_hard_safety_gate_missing_evidence(rules_engine):
    _, _, dec, _, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", None, {"status": "PASS"}, True, False)
    assert dec == "HUMAN_REVIEW"


def test_19_hard_safety_gate_mpn_mismatch(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified", "mpn_verified": False}
    _, _, dec, _, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "PASS"}, True, False)
    assert dec == "HUMAN_REVIEW"


def test_20_hard_safety_gate_mfg_mismatch(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified", "manufacturer_verified": False}
    _, _, dec, _, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "PASS"}, True, False)
    assert dec == "HUMAN_REVIEW"


def test_21_hard_safety_gate_validation_fail(rules_engine):
    ev = {"evidence_text": "txt", "status": "verified"}
    _, _, dec, _, _ = rules_engine.calculate_confidence("official_manufacturer_product_page", ev, {"status": "FAIL"}, True, False)
    assert dec == "HUMAN_REVIEW"


def test_22_confidence_engine_evaluate_attribute(confidence_engine):
    ev = {"evidence_text": "txt", "status": "verified", "evidence_id": "E1", "source_id": "S1"}
    conf = confidence_engine.evaluate_attribute("P1", "material", "Aluminum Oxide", "official_manufacturer_product_page", ev, {"status": "PASS"})
    assert conf.product_id == "P1"
    assert conf.confidence_score > 0.0
    assert conf.evidence_id == "E1"


def test_23_confidence_engine_evaluate_product_lowest_score(confidence_engine):
    c1 = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE")
    c2 = AttributeConfidence("P1", "grit", "P150", 0.70, 70, "REVIEW_RECOMMENDED")
    min_s, avg_s, auto_c, rec_c, rev_c = confidence_engine.evaluate_product("P1", [c1, c2])
    assert min_s == 0.70
    assert auto_c == 1 and rec_c == 1 and rev_c == 0


def test_24_confidence_engine_evaluate_product_average_score(confidence_engine):
    c1 = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.90, 90, "AUTO_APPROVE")
    c2 = AttributeConfidence("P1", "grit", "P150", 0.80, 80, "REVIEW_RECOMMENDED")
    min_s, avg_s, _, _, _ = confidence_engine.evaluate_product("P1", [c1, c2])
    assert avg_s == 0.85


def test_25_explainer_header_label(explainer):
    conf = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE", source_confidence=1.0, evidence_confidence=0.9, reason_codes=["OFFICIAL_MANUFACTURER_SOURCE"])
    exp = explainer.generate_explanation(conf)
    assert "Prodexa Confidence Score" in exp


def test_26_explainer_must_not_contain_ai_probability(explainer):
    conf = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE")
    exp = explainer.generate_explanation(conf)
    assert "AI Probability" not in exp
    assert "AI Confidence" not in exp


def test_27_confidence_registry_add_and_get():
    reg = ConfidenceRegistry()
    c1 = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE")
    reg.add_record(c1)
    res = reg.get_by_product("P1")
    assert len(res) == 1
    assert res[0].attribute_name == "material"


def test_28_confidence_registry_get_by_key():
    reg = ConfidenceRegistry()
    c1 = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE")
    reg.add_record(c1)
    res = reg.get_by_key("P1", "material")
    assert res is not None
    assert res.value == "Aluminum Oxide"


def test_29_confidence_registry_save_and_load_files(tmp_path):
    reg = ConfidenceRegistry()
    c1 = AttributeConfidence("P1", "material", "Aluminum Oxide", 0.95, 95, "AUTO_APPROVE")
    reg.add_record(c1)
    jsonl_p = str(tmp_path / "test_conf.jsonl")
    csv_p = str(tmp_path / "test_conf.csv")
    reg.save_jsonl(jsonl_p)
    reg.save_csv(csv_p)
    assert os.path.exists(jsonl_p)
    assert os.path.exists(csv_p)


def test_30_deterministic_repeatability(confidence_engine):
    ev = {"evidence_text": "txt", "status": "verified", "evidence_id": "E1", "source_id": "S1"}
    run_a = confidence_engine.evaluate_attribute("P100", "material", "Aluminum Oxide", "official_manufacturer_product_page", ev, {"status": "PASS"})
    run_b = confidence_engine.evaluate_attribute("P100", "material", "Aluminum Oxide", "official_manufacturer_product_page", ev, {"status": "PASS"})
    assert run_a.confidence_score == run_b.confidence_score
    assert run_a.decision == run_b.decision
    assert run_a.reason_codes == run_b.reason_codes
    assert run_a.source_confidence == run_b.source_confidence


def test_31_no_score_inflation_safeguard(confidence_engine):
    ev = {"source_type": "marketplace", "evidence_text": "", "status": "unverified", "confidence": 0.2}
    conf = confidence_engine.evaluate_attribute("P200", "material", "Unknown", "marketplace", ev, {"status": "FAIL"})
    assert conf.confidence_score < 0.50
    assert conf.decision == "HUMAN_REVIEW"


def test_32_immutability_verification():
    h = get_file_hashes()
    assert len(h) >= 17
    verified_cnt = verify_immutability(h)
    assert verified_cnt >= 17


def test_33_phase11_output_files_exist():
    assert os.path.exists("data/confidence/attribute_confidence.jsonl")
    assert os.path.exists("data/confidence/confidence_registry.csv")
    assert os.path.exists("data/processed/confidence_scored_products.csv")
    assert os.path.exists("reports/phase11_confidence_report.txt")
    assert os.path.exists("reports/phase11_confidence_audit.txt")


def test_34_confidence_scored_products_column_preservation():
    df_p10 = pd.read_csv("data/processed/validated_products.csv")
    df_p11 = pd.read_csv("data/processed/confidence_scored_products.csv")
    for col in df_p10.columns:
        assert col in df_p11.columns
    assert "confidence_status" in df_p11.columns


def test_35_attribute_confidence_jsonl_schema():
    with open("data/confidence/attribute_confidence.jsonl", "r", encoding="utf-8") as f:
        line = f.readline()
        assert line
        d = json.loads(line)
        assert "confidence_score" in d
        assert "decision" in d


def test_36_confidence_report_metrics():
    with open("reports/phase11_confidence_report.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "DATASET CONFIDENCE SUMMARY" in content
        assert "AUTO_APPROVE" in content


def test_37_adversarial_report_exists():
    with open("reports/phase11_confidence_audit.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "Adversarial Audit:                  PASS" in content or "Cases passed:                       32" in content


def test_38_threshold_clamping(confidence_engine):
    ev = {"evidence_text": "txt", "status": "verified"}
    conf = confidence_engine.evaluate_attribute("P1", "material", "Val", "official_manufacturer_product_page", ev, {"status": "PASS"})
    assert 0.00 <= conf.confidence_score <= 1.00


def test_39_reason_codes_populated(confidence_engine):
    ev = {"evidence_text": "txt", "status": "verified"}
    conf = confidence_engine.evaluate_attribute("P1", "material", "Val", "official_manufacturer_product_page", ev, {"status": "PASS"})
    assert len(conf.reason_codes) > 0


def test_40_final_acceptance_report_exists():
    with open("reports/phase11_confidence_audit.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "PASS" in content
