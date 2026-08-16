import os
import json
import pytest
import pandas as pd

from src.evidence.evidence_model import EvidenceRecord
from src.evidence.grounding_validator import GroundingValidator
from src.evidence.confidence_engine import ConfidenceEngine
from src.evidence.conflict_detector import ConflictDetector
from src.evidence.evidence_validator import EvidenceValidator
from src.evidence.evidence_registry import EvidenceRegistry
from src.evidence.evidence_view_model import EvidenceViewModelGenerator
from src.evidence.evidence_collector import EvidenceCollector
from src.evidence.phase9_pipeline import get_file_hashes, verify_immutability


@pytest.fixture(scope="module")
def grounding():
    return GroundingValidator()


@pytest.fixture(scope="module")
def confidence_engine():
    return ConfidenceEngine()


@pytest.fixture(scope="module")
def conflict_detector():
    return ConflictDetector()


@pytest.fixture(scope="module")
def validator():
    return EvidenceValidator()


@pytest.fixture(scope="module")
def sample_record():
    return EvidenceRecord(
        evidence_id="EV-0001",
        product_id="PROD-0001",
        attribute_name="material",
        value="Aluminum Oxide",
        source_id="SRC-001",
        source_url="https://www.3m.com/products/775l.pdf",
        source_type="manufacturer_pdf",
        source_title="3M Official Datasheet",
        manufacturer="3M",
        manufacturer_domain="3m.com",
        mpn="775L",
        normalized_mpn="775L",
        evidence_text="Abrasive Material: Aluminum Oxide",
        evidence_location="SPECIFICATIONS",
        page_number=1,
        section="SPECIFICATIONS",
        source_authority_score=1.0,
        mpn_verified=True,
        manufacturer_verified=True,
        lov_valid=True,
        uom_valid=True,
        normalized=True,
        validation_checks={"source_exists": True, "lov_valid": True},
        confidence=0.96,
        confidence_breakdown={"final_confidence": 0.96},
        conflict_status="none",
        manual_review_required=False,
        status="verified"
    )


def test_1_evidence_record_valid_instantiation(sample_record):
    assert sample_record.evidence_id == "EV-0001"
    assert sample_record.status == "verified"


def test_2_evidence_record_invalid_status_raises_error():
    with pytest.raises(ValueError):
        EvidenceRecord("E1", "P1", "a", "v", "s", "url", "t", "T", "M", "m.com", "MPN", "MPN", "e", "l", 1, "S", 1.0, True, True, True, True, True, {}, 0.9, {}, "none", False, "INVALID_STATUS")


def test_3_evidence_record_confidence_out_of_bounds_raises_error():
    with pytest.raises(ValueError):
        EvidenceRecord("E1", "P1", "a", "v", "s", "url", "t", "T", "M", "m.com", "MPN", "MPN", "e", "l", 1, "S", 1.0, True, True, True, True, True, {}, 1.5, {}, "none", False, "verified")


def test_4_evidence_record_to_dict(sample_record):
    d = sample_record.to_dict()
    assert isinstance(d, dict)
    assert d["evidence_id"] == "EV-0001"


def test_5_evidence_record_to_ui_view_model(sample_record):
    vm = sample_record.to_ui_view_model()
    assert vm["attribute"] == "Material"
    assert vm["confidence_percent"] == 96
    assert vm["source"]["manufacturer"] == "3M"


def test_6_grounding_validator_exact_match(grounding):
    ok, reason = grounding.validate_grounding("material", "Aluminum Oxide", "Abrasive Material: Aluminum Oxide")
    assert ok is True


def test_7_grounding_validator_numeric_match(grounding):
    ok, reason = grounding.validate_grounding("dimensions", "1/2 in x 18 in", "Dimensions: 1/2 in x 18 in")
    assert ok is True


def test_8_grounding_validator_grit_match(grounding):
    ok, reason = grounding.validate_grounding("grit", "P120", "Grit rating: 120 fine grit")
    assert ok is True


def test_9_grounding_validator_wattage_match(grounding):
    ok, reason = grounding.validate_grounding("wattage", "60W", "Wattage rating: 60 Watts")
    assert ok is True


def test_10_grounding_validator_rejection(grounding):
    ok, reason = grounding.validate_grounding("material", "Ceramic", "Material: PVC")
    assert ok is False


def test_11_confidence_engine_calculation(confidence_engine):
    score, breakdown, band = confidence_engine.calculate_confidence(1.0, True, True, True, True, True, False)
    assert score >= 0.90
    assert breakdown["mpn_match"] == 1.0


def test_12_confidence_engine_conflict_penalty(confidence_engine):
    score_normal, _, _ = confidence_engine.calculate_confidence(1.0, True, True, True, True, True, False)
    score_conflict, _, _ = confidence_engine.calculate_confidence(1.0, True, True, True, True, True, True)
    assert score_conflict < score_normal


def test_13_confidence_engine_clamping(confidence_engine):
    score, _, _ = confidence_engine.calculate_confidence(2.0, True, True, True, True, True, False)
    assert score <= 1.0


def test_14_conflict_detector_no_conflict_equal(conflict_detector):
    has_conf, _ = conflict_detector.check_conflict("material", "PVC", "PVC")
    assert has_conf is False


def test_15_conflict_detector_no_conflict_normalized(conflict_detector):
    has_conf, _ = conflict_detector.check_conflict("material", "Slate Gray", "slate-gray")
    assert has_conf is False


def test_16_conflict_detector_no_conflict_fraction_decimal(conflict_detector):
    has_conf, _ = conflict_detector.check_conflict("dimensions", "1/2 in x 18 in", "0.5 in x 18 in")
    assert has_conf is False


def test_17_conflict_detector_conflict_detected(conflict_detector):
    has_conf, _ = conflict_detector.check_conflict("material", "Stainless Steel", "Aluminum")
    assert has_conf is True


def test_18_evidence_validator_checks(validator):
    src = {"source_id": "S1", "url": "https://m.com", "manufacturer_verified": True, "mpn_verified": True}
    res = validator.validate_evidence("material", "PVC", src, "BLD_DECK_PVC", {"material"}, "Material: PVC")
    assert res["status"] == "verified"


def test_19_evidence_validator_missing_url(validator):
    src = {"source_id": "S1", "url": "", "manufacturer_verified": True, "mpn_verified": True}
    res = validator.validate_evidence("material", "PVC", src, "BLD_DECK_PVC", {"material"}, "Material: PVC")
    assert res["status"] == "unverified"


def test_20_evidence_validator_unverified_mpn(validator):
    src = {"source_id": "S1", "url": "https://m.com", "manufacturer_verified": True, "mpn_verified": False}
    res = validator.validate_evidence("material", "PVC", src, "BLD_DECK_PVC", {"material"}, "Material: PVC")
    assert res["status"] == "rejected"


def test_21_evidence_registry_add_and_get(sample_record):
    reg = EvidenceRegistry()
    assert reg.add_record(sample_record) is True
    assert reg.get_by_id("EV-0001") == sample_record


def test_22_evidence_registry_deduplication(sample_record):
    reg = EvidenceRegistry()
    reg.add_record(sample_record)
    assert reg.add_record(sample_record) is False
    assert reg.count() == 1


def test_23_evidence_registry_get_by_product(sample_record):
    reg = EvidenceRegistry()
    reg.add_record(sample_record)
    assert len(reg.get_by_product("PROD-0001")) == 1


def test_24_evidence_registry_get_by_attribute(sample_record):
    reg = EvidenceRegistry()
    reg.add_record(sample_record)
    assert len(reg.get_by_attribute("material")) == 1


def test_25_evidence_registry_get_by_mpn(sample_record):
    reg = EvidenceRegistry()
    reg.add_record(sample_record)
    assert len(reg.get_by_mpn("775L")) == 1


def test_26_evidence_registry_get_by_source(sample_record):
    reg = EvidenceRegistry()
    reg.add_record(sample_record)
    assert len(reg.get_by_source("SRC-001")) == 1


def test_27_evidence_registry_get_verified(sample_record):
    reg = EvidenceRegistry()
    reg.add_record(sample_record)
    assert len(reg.get_verified()) == 1


def test_28_evidence_registry_get_conflicts():
    reg = EvidenceRegistry()
    assert len(reg.get_conflicts()) == 0


def test_29_evidence_registry_save_and_load_jsonl(sample_record, tmp_path):
    p = str(tmp_path / "reg.jsonl")
    reg = EvidenceRegistry()
    reg.add_record(sample_record)
    reg.save_jsonl(p)
    assert os.path.exists(p)

    reg2 = EvidenceRegistry()
    reg2.load_jsonl(p)
    assert reg2.count() == 1
    assert reg2.get_by_id("EV-0001").product_id == "PROD-0001"


def test_30_evidence_view_model_generator(sample_record):
    gen = EvidenceViewModelGenerator()
    vm = gen.generate_view_model(sample_record)
    assert vm["attribute"] == "Material"
    assert vm["value"] == "Aluminum Oxide"


def test_31_evidence_collector_instantiation():
    collector = EvidenceCollector()
    assert collector is not None


def test_32_immutability_verification():
    h = get_file_hashes()
    assert len(h) == 13
    verify_immutability(h)


def test_33_phase9_pipeline_output_files_exist():
    assert os.path.exists("data/evidence/evidence_registry.jsonl")
    assert os.path.exists("data/evidence/attribute_evidence.csv")
    assert os.path.exists("data/processed/evidence_enriched_products.csv")
    assert os.path.exists("reports/phase9_evidence_report.txt")
    assert os.path.exists("reports/phase9_evidence_audit.txt")


def test_34_phase9_column_preservation():
    df_p81 = pd.read_csv("data/processed/enriched_products_phase8_1.csv")
    df_p9 = pd.read_csv("data/processed/evidence_enriched_products.csv")
    for col in df_p81.columns:
        assert col in df_p9.columns


def test_35_evidence_coverage_non_zero():
    df_p9 = pd.read_csv("data/processed/evidence_enriched_products.csv")
    assert (df_p9["evidence_count"] > 0).sum() > 0
