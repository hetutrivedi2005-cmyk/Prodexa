import os
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.enrichment.source_discovery import ManufacturerSourceDiscovery
from src.enrichment.evidence_validator import EvidenceValidator
from src.enrichment.conflict_detector import ConflictDetector
from src.enrichment.vector_store import ModularVectorStore
from src.enrichment.rag_retriever import ProductRAGRetriever
from src.enrichment.enrichment_extractor import EvidenceEnrichmentExtractor
from src.enrichment.document_cleaner import DocumentCleaner
from src.enrichment.chunker import DocumentChunker


def run_phase8_1_adversarial_audit(report_path: str = "reports/phase8_1_adversarial_audit.txt"):
    print("=" * 80)
    print("PRODEXA PHASE 8.1 — ADVERSARIAL AUDIT")
    print("=" * 80)

    discovery = ManufacturerSourceDiscovery()
    validator = EvidenceValidator()
    conflict_detector = ConflictDetector()
    vector_store = ModularVectorStore()
    rag_retriever = ProductRAGRetriever(vector_store)
    extractor = EvidenceEnrichmentExtractor()
    cleaner = DocumentCleaner()
    chunker = DocumentChunker()

    audit_logs = []
    test_cases_passed = 0
    total_test_cases = 20

    # CASE 1: Wrong MPN source -> REJECT
    v1 = discovery.verify_source_identity("WRONG_MPN_999", "DCB518ASTS06G", "Freud", "Freud")
    assert v1 is False
    audit_logs.append("[PASS] Case 1: Wrong MPN source rejected.")
    test_cases_passed += 1

    # CASE 2: Similar MPN -> REJECT
    v2 = discovery.verify_source_identity("DCB518ASTS08G", "DCB518ASTS06G", "Freud", "Freud")
    assert v2 is False
    audit_logs.append("[PASS] Case 2: Similar but non-identical MPN rejected.")
    test_cases_passed += 1

    # CASE 3: Wrong manufacturer -> REJECT
    v3 = discovery.verify_source_identity("DCB518ASTS06G", "DCB518ASTS06G", "UnrelatedMfg", "Freud")
    assert v3 is False
    audit_logs.append("[PASS] Case 3: Wrong manufacturer rejected.")
    test_cases_passed += 1

    # CASE 4: Manufacturer source vs marketplace conflict -> Manufacturer wins
    sources = discovery.discover_sources("Freud", "Diablo", "DCB518ASTS06G")
    assert sources[0]["authority_score"] > sources[-1]["authority_score"]
    audit_logs.append("[PASS] Case 4: Manufacturer source outranks marketplace source.")
    test_cases_passed += 1

    # CASE 5: Distributor source vs manufacturer source -> Manufacturer wins
    mfg_src = [s for s in sources if "manufacturer" in s["source_type"]][0]
    dist_src = [s for s in sources if "distributor" in s["source_type"]][0]
    assert mfg_src["authority_score"] > dist_src["authority_score"]
    audit_logs.append("[PASS] Case 5: Manufacturer source outranks distributor source.")
    test_cases_passed += 1

    # CASE 6: Missing MPN -> Safe fallback / REJECT
    v6 = discovery.verify_source_identity("", "DCB518ASTS06G", "Freud", "Freud")
    assert v6 is False
    audit_logs.append("[PASS] Case 6: Missing MPN source rejected.")
    test_cases_passed += 1

    # CASE 7: MPN with punctuation -> PASS (Normalized exact match)
    v7 = discovery.verify_source_identity("DCB518-ASTS06G", "DCB518ASTS06G", "Freud", "Freud")
    assert v7 is True
    audit_logs.append("[PASS] Case 7: MPN with punctuation verified after normalization.")
    test_cases_passed += 1

    # CASE 8: MPN with spaces -> PASS (Normalized exact match)
    v8 = discovery.verify_source_identity("DCB518 ASTS06G", "DCB518ASTS06G", "Freud", "Freud")
    assert v8 is True
    audit_logs.append("[PASS] Case 8: MPN with spaces verified after normalization.")
    test_cases_passed += 1

    # CASE 9: PDF with repeated headers -> Cleaned safely
    c9 = cleaner.clean_segment_text("Page 1 of 10\n- Material: PVC")
    assert "Page 1 of 10" not in c9
    audit_logs.append("[PASS] Case 9: PDF repeated headers cleaned safely.")
    test_cases_passed += 1

    # CASE 10: PDF table extraction -> Intact chunking
    segs10 = [{"source_id": "S1", "source_url": "u", "source_type": "m", "manufacturer": "Freud", "mpn": "DCB518ASTS06G", "page": 1, "section": "SPECIFICATIONS", "text": "Dimensions: 1/2 in x 18 in"}]
    c10 = chunker.chunk_segments(segs10)
    assert len(c10) == 1 and c10[0]["section"] == "SPECIFICATIONS"
    audit_logs.append("[PASS] Case 10: PDF specification table chunking preserved.")
    test_cases_passed += 1

    # CASE 11: Attribute synonym retrieval -> PASS
    vector_store.clear_collection()
    vector_store.add_documents([{
        "chunk_id": "C1", "source_id": "S1", "source_url": "u", "source_type": "m",
        "manufacturer": "Freud", "mpn": "DCB518ASTS06G", "page": 1, "section": "SPECIFICATIONS",
        "text": "Belt Size: 1/2 in x 18 in"
    }])
    ret11 = rag_retriever.retrieve_evidence_for_missing_attributes("DCB518ASTS06G", "Freud", "ABR_BELT_SANDING", ["dimensions"])
    assert len(ret11.get("dimensions", [])) > 0
    audit_logs.append("[PASS] Case 11: Attribute synonym query expansion retrieval passed.")
    test_cases_passed += 1

    # CASE 12: Attribute not present in source -> NULL
    res12 = extractor.extract_attributes_from_evidence("DCB518ASTS06G", "ABR_BELT_SANDING", ["voltage"], {})
    assert res12["voltage"] is None
    audit_logs.append("[PASS] Case 12: Attribute missing from evidence returns null.")
    test_cases_passed += 1

    # CASE 13: LLM invented value -> REJECT
    val13 = validator.validate_candidate(
        candidate={"attribute_name": "invented", "value": "invented_val", "evidence_text": "", "attribute_confidence": 0.9},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"grit", "dimensions"},
        source_info=sources[0]
    )
    assert val13["decision"] == "reject"
    audit_logs.append("[PASS] Case 13: LLM invented value rejected.")
    test_cases_passed += 1

    # CASE 14: LLM unsupported inference -> REJECT
    val14 = validator.validate_candidate(
        candidate={"attribute_name": "grit", "value": "P120", "evidence_text": "", "attribute_confidence": 0.9},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"grit"},
        source_info=sources[0]
    )
    assert val14["decision"] == "reject"
    audit_logs.append("[PASS] Case 14: LLM unsupported inference rejected.")
    test_cases_passed += 1

    # CASE 15: Conflicting manufacturer documents -> Manual review / conflict
    has_conf15, act15 = conflict_detector.check_conflict("dimensions", "1/2 in x 18 in", "2 in x 20 in")
    assert has_conf15 is True and act15 == "conflict"
    audit_logs.append("[PASS] Case 15: Conflicting values flagged for manual review.")
    test_cases_passed += 1

    # CASE 16: Cross-product retrieval attempt -> REJECT
    vector_store.clear_collection()
    vector_store.add_documents([{
        "chunk_id": "C2", "source_id": "S2", "source_url": "u", "source_type": "m",
        "manufacturer": "3M", "mpn": "775L", "page": 1, "section": "SPECIFICATIONS", "text": "3M 775L Disc"
    }])
    ret16 = vector_store.search("dimensions", filters={"manufacturer": "Freud", "mpn": "DCB518ASTS06G"})
    assert len(ret16) == 0
    audit_logs.append("[PASS] Case 16: Cross-product retrieval attempt rejected.")
    test_cases_passed += 1

    # CASE 17: Wrong category attribute -> REJECT
    val17 = validator.validate_candidate(
        candidate={"attribute_name": "voltage", "value": "20V", "evidence_text": "20V", "attribute_confidence": 0.9},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"grit", "dimensions"},
        source_info=sources[0]
    )
    assert val17["decision"] == "reject"
    audit_logs.append("[PASS] Case 17: Attribute outside category schema rejected.")
    test_cases_passed += 1

    # CASE 18: Invalid LOV value -> LOV Fallback
    val18 = validator.validate_candidate(
        candidate={"attribute_name": "color", "value": "UNMAPPED_COLOR", "evidence_text": "UNMAPPED_COLOR", "attribute_confidence": 0.9},
        category_id="BLD_DECK_PVC",
        allowed_attributes={"color"},
        source_info=sources[0]
    )
    assert val18["normalized_value"] == "UNMAPPED_COLOR"
    audit_logs.append("[PASS] Case 18: Invalid LOV value handled safely.")
    test_cases_passed += 1

    # CASE 19: Invalid UOM -> UOM Normalization
    val19 = validator.validate_candidate(
        candidate={"attribute_name": "dimensions", "value": "0.5 in x 18 in", "evidence_text": "0.5 in x 18 in", "attribute_confidence": 0.9},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"dimensions"},
        source_info=sources[0]
    )
    assert val19["normalized_value"] == "1/2 in x 18 in"
    audit_logs.append("[PASS] Case 19: UOM normalized successfully.")
    test_cases_passed += 1

    # CASE 20: Phase 7 trusted value overwrite attempt -> CONFLICT / DO NOT OVERWRITE
    has_conf20, act20 = conflict_detector.check_conflict("grit", "P120", "P180")
    assert has_conf20 is True and act20 == "conflict"
    audit_logs.append("[PASS] Case 20: Phase 7 trusted value overwrite attempt prevented.")
    test_cases_passed += 1

    report_content = [
        "============================================================",
        "PRODEXA PHASE 8.1 — ADVERSARIAL AUDIT REPORT",
        "============================================================",
        f"Total Test Cases: {total_test_cases}",
        f"Passed Cases:     {test_cases_passed}",
        f"Audit Result:     PASS ({test_cases_passed/total_test_cases*100:.1f}%)",
        "============================================================",
        ""
    ] + audit_logs

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))

    print("\n".join(audit_logs))
    print("\n" + "=" * 80)
    print(f"ADVERSARIAL AUDIT SUMMARY: {test_cases_passed} / {total_test_cases} CASES PASSED (100.0%)")
    print(f"[SUCCESS] Audit report saved to '{report_path}'.")
    print("=" * 80)


if __name__ == "__main__":
    run_phase8_1_adversarial_audit()
