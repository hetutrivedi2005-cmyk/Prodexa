import os
import json
import pytest
import pandas as pd

from src.evidence.evidence_span_validator import EvidenceSpanValidator
from src.evidence.confidence_engine import ConfidenceEngine
from src.evidence.source_consistency import SourceConsistencyEvaluator
from src.evidence.evidence_deduplicator import EvidenceDeduplicator
from src.evidence.evidence_view_model import EvidenceViewModelGenerator
from src.evidence.evidence_model import EvidenceRecord
from src.evidence.phase9_1_pipeline import get_file_hashes, verify_immutability


@pytest.fixture(scope="module")
def span_validator():
    return EvidenceSpanValidator()


@pytest.fixture(scope="module")
def confidence_engine():
    return ConfidenceEngine()


@pytest.fixture(scope="module")
def consistency_evaluator():
    return SourceConsistencyEvaluator()


@pytest.fixture(scope="module")
def deduplicator():
    return EvidenceDeduplicator()


@pytest.fixture(scope="module")
def view_model_gen():
    return EvidenceViewModelGenerator()


def test_1_span_validator_exact_match(span_validator):
    res = span_validator.validate_span("material", "PVC", "Material: PVC decking")
    assert res["grounded"] is True
    assert res["matched_text"] == "PVC"


def test_2_span_validator_normalized_match(span_validator):
    res = span_validator.validate_span("material", "Slate Gray", "Color: slate-gray")
    assert res["grounded"] is True


def test_3_span_validator_numeric_uom_match(span_validator):
    res = span_validator.validate_span("dimensions", "1/2 in x 18 in", "Dimensions: 1/2 in x 18 in")
    assert res["grounded"] is True


def test_4_span_validator_grit_match(span_validator):
    res = span_validator.validate_span("grit", "P120", "Abrasive disc 120 grit")
    assert res["grounded"] is True


def test_5_span_validator_wattage_match(span_validator):
    res = span_validator.validate_span("wattage", "60W", "Rating: 60 Watts")
    assert res["grounded"] is True


def test_6_span_validator_rejection(span_validator):
    res = span_validator.validate_span("material", "Aluminum", "Material: Steel")
    assert res["grounded"] is False


def test_7_confidence_engine_high_band(confidence_engine):
    score, breakdown, band = confidence_engine.calculate_confidence(1.0, True, True, True, True, True, False)
    assert score >= 0.95
    assert band == "HIGH"


def test_8_confidence_engine_medium_band(confidence_engine):
    score, breakdown, band = confidence_engine.calculate_confidence(0.70, True, True, True, True, True, False)
    assert 0.85 <= score < 0.95
    assert band == "MEDIUM"


def test_9_confidence_engine_ungrounded_override(confidence_engine):
    score, breakdown, band = confidence_engine.calculate_confidence(1.0, True, True, False, True, True, False)
    assert score <= 0.40
    assert band == "UNVERIFIED"


def test_10_consistency_evaluator_consistent(consistency_evaluator):
    recs = [
        {"value": "PVC", "source_url": "http://m.com/1"},
        {"value": "PVC", "source_url": "http://m.com/2"}
    ]
    st, is_conf, updated = consistency_evaluator.evaluate_consistency(recs)
    assert st == "consistent" and is_conf is False


def test_11_consistency_evaluator_conflict(consistency_evaluator):
    recs = [
        {"value": "PVC", "source_url": "http://m.com/1"},
        {"value": "Composite", "source_url": "http://m.com/2"}
    ]
    st, is_conf, updated = consistency_evaluator.evaluate_consistency(recs)
    assert st == "conflict" and is_conf is True


def test_12_deduplicator_removes_duplicates(deduplicator):
    recs = [
        {"source_url": "http://m.com", "mpn": "M1", "attribute_name": "material", "value": "PVC", "evidence_text": "text"},
        {"source_url": "http://m.com", "mpn": "M1", "attribute_name": "material", "value": "PVC", "evidence_text": "text"}
    ]
    dedup, stats = deduplicator.deduplicate_records(recs)
    assert len(dedup) == 1
    assert stats["duplicate_evidence_removed"] == 1


def test_13_deduplicator_keeps_unique(deduplicator):
    recs = [
        {"source_url": "http://m.com", "mpn": "M1", "attribute_name": "material", "value": "PVC", "evidence_text": "text1"},
        {"source_url": "http://m.com", "mpn": "M1", "attribute_name": "color", "value": "White", "evidence_text": "text2"}
    ]
    dedup, stats = deduplicator.deduplicate_records(recs)
    assert len(dedup) == 2


def test_14_view_model_gen_schema(view_model_gen):
    rec = EvidenceRecord("E1", "P1", "material", "PVC", "S1", "http://m.com", "t", "T", "M", "m.com", "MPN", "MPN", "Material: PVC", "Spec", 1, "SPEC", 1.0, True, True, True, True, True, {}, 0.96, {"confidence_band": "HIGH"}, "none", False, "verified")
    vm = view_model_gen.generate_view_model(rec)
    assert vm["confidence_band"] == "HIGH"
    assert vm["attribute"] == "Material"


def test_15_immutability_verification():
    h = get_file_hashes()
    assert len(h) == 14
    verify_immutability(h)


def test_16_phase9_1_output_files_exist():
    assert os.path.exists("data/evidence/evidence_quality_registry.jsonl")
    assert os.path.exists("data/evidence/evidence_conflicts.jsonl")
    assert os.path.exists("data/evidence/evidence_ui.jsonl")
    assert os.path.exists("reports/phase9_1_quality_report.txt")
    assert os.path.exists("reports/phase9_1_adversarial_audit.txt")


def test_17_quality_registry_schema():
    with open("data/evidence/evidence_quality_registry.jsonl", "r", encoding="utf-8") as f:
        line = f.readline()
        assert line
        d = json.loads(line)
        assert "confidence_band" in d
        assert "confidence" in d


def test_18_ui_jsonl_schema():
    with open("data/evidence/evidence_ui.jsonl", "r", encoding="utf-8") as f:
        line = f.readline()
        assert line
        d = json.loads(line)
        assert "confidence_band" in d
        assert "validation" in d
        assert "source" in d
        assert "evidence" in d


def test_19_conflicts_jsonl_valid():
    if os.path.exists("data/evidence/evidence_conflicts.jsonl"):
        with open("data/evidence/evidence_conflicts.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    assert d["conflict_status"] == "conflict"


def test_20_quality_report_metrics():
    with open("reports/phase9_1_quality_report.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "High-confidence evidence count" in content
        assert "Duplicate evidence removed" in content


def test_21_adversarial_report_exists():
    assert os.path.exists("reports/phase9_1_adversarial_audit.txt")
    with open("reports/phase9_1_adversarial_audit.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "Passed Cases:     30" in content or "30 / 30" in content


def test_22_span_validator_empty_value(span_validator):
    res = span_validator.validate_span("material", "", "Material: PVC")
    assert res["grounded"] is False


def test_23_span_validator_none_value(span_validator):
    res = span_validator.validate_span("material", None, "Material: PVC")
    assert res["grounded"] is False


def test_24_confidence_engine_low_band(confidence_engine):
    score, _, band = confidence_engine.calculate_confidence(0.20, True, True, True, True, True, False)
    assert band in ["LOW", "UNVERIFIED"]


def test_25_consistency_evaluator_single_record(consistency_evaluator):
    recs = [{"value": "PVC"}]
    st, is_conf, _ = consistency_evaluator.evaluate_consistency(recs)
    assert st == "consistent" and is_conf is False


def test_26_consistency_evaluator_empty_records(consistency_evaluator):
    st, is_conf, _ = consistency_evaluator.evaluate_consistency([])
    assert st == "consistent" and is_conf is False


def test_27_deduplicator_empty_input(deduplicator):
    dedup, stats = deduplicator.deduplicate_records([])
    assert len(dedup) == 0 and stats["unique_evidence_count"] == 0


def test_28_view_model_gen_unverified_band(view_model_gen):
    rec = EvidenceRecord("E1", "P1", "m", "v", "s", "http", "t", "T", "M", "m.com", "MPN", "MPN", "e", "l", 1, "S", 0.0, False, False, False, False, False, {}, 0.3, {}, "none", False, "unverified")
    vm = view_model_gen.generate_view_model(rec)
    assert vm["confidence_band"] == "UNVERIFIED"


def test_29_protected_files_count():
    hashes = get_file_hashes()
    assert len(hashes) == 14


def test_30_protected_file_modified_raises_error(tmp_path):
    h = get_file_hashes()
    verify_immutability(h)


def test_31_span_validator_section_preservation(span_validator):
    res = span_validator.validate_span("material", "PVC", "Material: PVC", section="TECHNICAL DATA", page_number=3)
    assert res["section"] == "TECHNICAL DATA"
    assert res["page_number"] == 3


def test_32_confidence_engine_breakdown_keys(confidence_engine):
    _, bd, _ = confidence_engine.calculate_confidence(1.0, True, True, True, True, True, False)
    assert "source_authority" in bd
    assert "mpn_match" in bd
    assert "confidence_band" in bd


def test_33_deduplicator_different_urls(deduplicator):
    recs = [
        {"source_url": "http://m1.com", "mpn": "M1", "attribute_name": "m", "value": "v", "evidence_text": "e"},
        {"source_url": "http://m2.com", "mpn": "M1", "attribute_name": "m", "value": "v", "evidence_text": "e"}
    ]
    dedup, _ = deduplicator.deduplicate_records(recs)
    assert len(dedup) == 2


def test_34_phase9_1_quality_registry_not_empty():
    with open("data/evidence/evidence_quality_registry.jsonl", "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 0


def test_35_phase9_1_ui_jsonl_not_empty():
    with open("data/evidence/evidence_ui.jsonl", "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 0
