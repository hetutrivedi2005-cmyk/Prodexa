import os
import json
import pytest
import tempfile
import pandas as pd

from src.review.review_model import ReviewItem, ReviewAuditRecord
from src.review.review_queue import ReviewQueueEngine
from src.review.review_service import ReviewService
from src.review.review_audit import ReviewAuditLogger
from src.review.phase12_pipeline import get_file_hashes, verify_immutability


@pytest.fixture(scope="module")
def queue_engine():
    return ReviewQueueEngine()


def test_1_review_item_valid_instantiation():
    item = ReviewItem("R1", "P1", "material", "Val", "Val", 0.6, "HUMAN_REVIEW", "PASS", "PENDING", "HIGH")
    assert item.review_id == "R1"
    assert item.confidence_score == 0.6


def test_2_review_item_invalid_status_raises_error():
    with pytest.raises(ValueError):
        ReviewItem("R1", "P1", "material", "Val", "Val", 0.6, "HUMAN_REVIEW", "PASS", "INVALID_STATUS")


def test_3_review_item_invalid_action_raises_error():
    with pytest.raises(ValueError):
        ReviewItem("R1", "P1", "material", "Val", "Val", 0.6, "HUMAN_REVIEW", "PASS", "PENDING", "HIGH", review_action="INVALID_ACTION")


def test_4_review_item_to_dict():
    item = ReviewItem("R1", "P1", "material", "Val", "Val", 0.6, "HUMAN_REVIEW", "PASS")
    d = item.to_dict()
    assert isinstance(d, dict)
    assert d["review_id"] == "R1"


def test_5_review_audit_record_valid_instantiation():
    rec = ReviewAuditRecord("A1", "R1", "P1", "material", "ACCEPT", "Val", "Val", "rev1", "Reason", "PASS", 0.6, 1.0)
    assert rec.audit_id == "A1"
    assert rec.action == "ACCEPT"


def test_6_review_audit_record_invalid_action_raises_error():
    with pytest.raises(ValueError):
        ReviewAuditRecord("A1", "R1", "P1", "material", "BAD_ACTION", "Val", "Val", "rev1", "Reason", "PASS", 0.6, 1.0)


def test_7_queue_engine_validation_fail(queue_engine):
    req, prio, r = queue_engine.should_enter_queue(0.95, "AUTO_APPROVE", "FAIL", None, [])
    assert req is True
    assert prio == "HIGH"


def test_8_queue_engine_low_confidence(queue_engine):
    req, prio, r = queue_engine.should_enter_queue(0.55, "HUMAN_REVIEW", "PASS", None, ["LOW_CONFIDENCE"])
    assert req is True
    assert prio == "HIGH"


def test_9_queue_engine_missing_evidence(queue_engine):
    req, prio, r = queue_engine.should_enter_queue(0.85, "REVIEW_RECOMMENDED", "PASS", None, ["MISSING_EVIDENCE"])
    assert req is True


def test_10_queue_engine_conflict(queue_engine):
    req, prio, r = queue_engine.should_enter_queue(0.60, "HUMAN_REVIEW", "PASS", {"conflict_status": "conflict"}, [])
    assert req is True
    assert prio == "HIGH"


def test_11_queue_engine_generate_queue_sorting(queue_engine):
    conf_recs = [
        {"product_id": "P1", "attribute_name": "grit", "value": "P150", "confidence_score": 0.85, "decision": "REVIEW_RECOMMENDED"},
        {"product_id": "P2", "attribute_name": "material", "value": "Val", "confidence_score": 0.40, "decision": "HUMAN_REVIEW"}
    ]
    q = queue_engine.generate_queue(conf_recs, {}, {})
    assert len(q) == 2
    assert q[0].confidence_score == 0.40  # Lowest confidence / HIGH priority first


def test_12_review_service_load_queue_and_get_queue():
    service = ReviewService()
    item = ReviewItem("R12", "P12", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
    service.load_queue([item])
    res = service.get_review_queue()
    assert len(res) == 1
    assert res[0].review_id == "R12"


def test_13_review_service_status_filter():
    service = ReviewService()
    item1 = ReviewItem("R13_1", "P13", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS", "PENDING")
    item2 = ReviewItem("R13_2", "P13", "grit", "P150", "P150", 0.5, "HUMAN_REVIEW", "PASS", "APPROVED")
    service.load_queue([item1, item2])
    pend = service.get_review_queue("PENDING")
    assert len(pend) == 1 and pend[0].review_id == "R13_1"


def test_14_review_service_get_review_item():
    service = ReviewService()
    item = ReviewItem("R14", "P14", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
    service.load_queue([item])
    assert service.get_review_item("R14") is not None
    assert service.get_review_item("NON_EXISTENT") is None


def test_15_review_service_get_product_review():
    service = ReviewService()
    item1 = ReviewItem("R15_1", "P15", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
    item2 = ReviewItem("R15_2", "P15", "grit", "P150", "P150", 0.5, "HUMAN_REVIEW", "PASS")
    service.load_queue([item1, item2])
    res = service.get_product_review("P15")
    assert len(res) == 2


def test_16_review_service_get_attribute_review():
    service = ReviewService()
    item = ReviewItem("R16", "P16", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
    service.load_queue([item])
    res = service.get_attribute_review("P16", "material")
    assert res is not None and res.review_id == "R16"


def test_17_review_service_validate_human_edit_valid_pass():
    service = ReviewService()
    is_valid, msg = service.validate_human_edit("material", "Aluminum")
    assert is_valid is True


def test_18_review_service_validate_human_edit_empty_fail():
    service = ReviewService()
    is_valid, msg = service.validate_human_edit("material", "   ")
    assert is_valid is False
    assert "cannot be empty" in msg


def test_19_review_service_validate_human_edit_char_limit_fail():
    service = ReviewService()
    is_valid, msg = service.validate_human_edit("invoice_description", "X" * 150)
    assert is_valid is False
    assert "exceeded maximum allowed limit" in msg


def test_20_review_service_validate_human_edit_invalid_lov_fail():
    service = ReviewService()
    is_valid, msg = service.validate_human_edit("material", "Unapproved Shiny Plastic")
    assert is_valid is False
    assert "not present in attribute_lov.csv" in msg


def test_21_review_service_validate_human_edit_valid_lov_pass():
    service = ReviewService()
    is_valid, msg = service.validate_human_edit("material", "Stainless Steel")
    assert is_valid is True


def test_22_review_service_validate_human_edit_invalid_uom_fail():
    service = ReviewService()
    is_valid, msg = service.validate_human_edit("dimensions", "10 lightyears")
    assert is_valid is False


def test_23_review_service_validate_human_edit_valid_uom_pass():
    service = ReviewService()
    is_valid, msg = service.validate_human_edit("dimensions", "15 in")
    assert is_valid is True


def test_24_review_service_approve_review_accept():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R24", "P24", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        res = service.approve_review("R24", "rev1", "Accepted")
        assert res.review_status == "APPROVED"
        assert res.review_action == "ACCEPT"


def test_25_review_service_approve_already_resolved_raises_error():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R25", "P25", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        service.approve_review("R25", "rev1", "Accepted")
        with pytest.raises(ValueError):
            service.approve_review("R25", "rev1", "Approve again")


def test_26_review_service_edit_review_edit():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R26", "P26", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        res = service.edit_review("R26", "Stainless Steel", "rev1", "Edited")
        assert res.review_status == "EDITED"
        assert res.proposed_value == "Stainless Steel"


def test_27_review_service_edit_invalid_lov_raises_error():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R27", "P27", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        with pytest.raises(ValueError):
            service.edit_review("R27", "Invalid LOV Material", "rev1", "Bad edit")


def test_28_review_service_edit_invalid_uom_raises_error():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R28", "P28", "dimensions", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        with pytest.raises(ValueError):
            service.edit_review("R28", "10 lightyears", "rev1", "Bad UOM")


def test_29_review_service_reject_review():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R29", "P29", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        res = service.reject_review("R29", "rev1", "Rejection comment")
        assert res.review_status == "REJECTED"


def test_30_review_service_reject_missing_comment_raises_error():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R30", "P30", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        with pytest.raises(ValueError):
            service.reject_review("R30", "rev1", "   ")


def test_31_review_service_escalate_review():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R31", "P31", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        res = service.escalate_review("R31", "rev1", "Escalation comment")
        assert res.review_status == "ESCALATED"


def test_32_review_service_escalate_missing_comment_raises_error():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item = ReviewItem("R32", "P32", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item])
        with pytest.raises(ValueError):
            service.escalate_review("R32", "rev1", "")


def test_33_review_audit_logger_save_and_read(tmp_path):
    fpath = str(tmp_path / "audit.jsonl")
    logger = ReviewAuditLogger(fpath)
    rec = ReviewAuditRecord("A33", "R33", "P33", "material", "ACCEPT", "v1", "v1", "rev1", "reason", "PASS", 0.5, 1.0)
    logger.log_action(rec)
    hist = logger.get_audit_history()
    assert len(hist) == 1
    assert hist[0].audit_id == "A33"


def test_34_review_audit_logger_filter_by_product(tmp_path):
    fpath = str(tmp_path / "audit.jsonl")
    logger = ReviewAuditLogger(fpath)
    rec1 = ReviewAuditRecord("A1", "R1", "P34", "material", "ACCEPT", "v1", "v1", "rev1", "reason", "PASS", 0.5, 1.0)
    rec2 = ReviewAuditRecord("A2", "R2", "P99", "material", "ACCEPT", "v2", "v2", "rev1", "reason", "PASS", 0.5, 1.0)
    logger.log_action(rec1)
    logger.log_action(rec2)
    hist = logger.get_audit_history("P34")
    assert len(hist) == 1
    assert hist[0].product_id == "P34"


def test_35_review_service_statistics():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        item1 = ReviewItem("R1", "P1", "material", "Val", "Val", 0.5, "HUMAN_REVIEW", "PASS")
        item2 = ReviewItem("R2", "P2", "grit", "P150", "P150", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([item1, item2])
        service.approve_review("R1", "rev1", "Approve")
        stats = service.get_review_statistics()
        assert stats["total_items"] == 2
        assert stats["approved"] == 1
        assert stats["pending_reviews"] == 1


def test_36_protected_files_immutability():
    h = get_file_hashes()
    assert len(h) >= 17
    verified_cnt = verify_immutability(h)
    assert verified_cnt >= 17


def test_37_output_artifact_1_review_queue_jsonl():
    assert os.path.exists("data/review/review_queue.jsonl")


def test_38_output_artifact_2_review_audit_jsonl():
    assert os.path.exists("data/review/review_audit.jsonl")


def test_39_output_artifact_3_review_registry_csv():
    assert os.path.exists("data/review/review_registry.csv")


def test_40_output_artifact_4_human_reviewed_products_csv():
    assert os.path.exists("data/processed/human_reviewed_products.csv")
    df = pd.read_csv("data/processed/human_reviewed_products.csv")
    assert "human_review_status" in df.columns


def test_41_output_artifact_5_review_report():
    with open("reports/phase12_review_report.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "DASHBOARD & WORKFLOW METRICS" in content


def test_42_output_artifact_6_review_audit():
    with open("reports/phase12_review_audit.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "PHASE 12 SYSTEM STATUS:             PASS" in content


def test_43_output_artifact_7_final_acceptance():
    with open("reports/phase12_final_acceptance.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "PHASE 12 SYSTEM STATUS:             PASS" in content
        assert "HUMAN REVIEW QUEUE STATUS:          PENDING" in content


def test_44_audit_trail_integrity():
    assert os.path.exists("data/review/review_audit.jsonl")


def test_45_full_end_to_end_review_workflow():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fpath = os.path.join(tmp_dir, "audit.jsonl")
        service = ReviewService(audit_filepath=fpath)
        i1 = ReviewItem("R1", "P1", "material", "v1", "v1", 0.5, "HUMAN_REVIEW", "PASS")
        i2 = ReviewItem("R2", "P2", "material", "v2", "v2", 0.5, "HUMAN_REVIEW", "PASS")
        i3 = ReviewItem("R3", "P3", "material", "v3", "v3", 0.5, "HUMAN_REVIEW", "PASS")
        i4 = ReviewItem("R4", "P4", "material", "v4", "v4", 0.5, "HUMAN_REVIEW", "PASS")
        service.load_queue([i1, i2, i3, i4])

        service.approve_review("R1", "r1", "Ok")
        service.edit_review("R2", "Stainless Steel", "r1", "Ok edit")
        service.reject_review("R3", "r1", "Reject reason")
        service.escalate_review("R4", "r1", "Escalate reason")

        stats = service.get_review_statistics()
        assert stats["approved"] == 1
        assert stats["edited"] == 1
        assert stats["rejected"] == 1
        assert stats["escalated"] == 1
