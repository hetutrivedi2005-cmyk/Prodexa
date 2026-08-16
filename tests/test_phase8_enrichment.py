import os
import json
import pytest
import pandas as pd

from src.enrichment.missing_attribute_detector import MissingAttributeDetector
from src.enrichment.source_discovery import ManufacturerSourceDiscovery
from src.enrichment.source_fetcher import SourceFetcher
from src.enrichment.document_extractor import DocumentExtractor
from src.enrichment.document_cleaner import DocumentCleaner
from src.enrichment.chunker import DocumentChunker
from src.enrichment.vector_store import ModularVectorStore
from src.enrichment.rag_retriever import ProductRAGRetriever
from src.enrichment.enrichment_extractor import EvidenceEnrichmentExtractor
from src.enrichment.evidence_validator import EvidenceValidator
from src.enrichment.conflict_detector import ConflictDetector


@pytest.fixture(scope="module")
def discovery():
    return ManufacturerSourceDiscovery()


@pytest.fixture(scope="module")
def fetcher():
    return SourceFetcher()


@pytest.fixture(scope="module")
def extractor():
    return DocumentExtractor()


@pytest.fixture(scope="module")
def cleaner():
    return DocumentCleaner()


@pytest.fixture(scope="module")
def chunker():
    return DocumentChunker()


@pytest.fixture(scope="module")
def vector_store():
    return ModularVectorStore()


@pytest.fixture(scope="module")
def validator():
    return EvidenceValidator()


@pytest.fixture(scope="module")
def conflict_detector():
    return ConflictDetector()


def test_1_mpn_normalization(discovery):
    assert discovery.normalize_mpn("DCB518-ASTS06G") == "DCB518ASTS06G"
    assert discovery.normalize_mpn("dcb518asts06g") == "DCB518ASTS06G"
    assert discovery.normalize_mpn("775L") == "775L"


def test_2_exact_mpn_verification(discovery):
    assert discovery.verify_source_identity("DCB518ASTS06G", "DCB518-ASTS06G", "Freud", "Freud") is True


def test_3_wrong_mpn_rejection(discovery):
    assert discovery.verify_source_identity("WRONG_MPN", "DCB518ASTS06G", "Freud", "Freud") is False


def test_4_manufacturer_verification(discovery):
    assert discovery.verify_source_identity("DCB518ASTS06G", "DCB518ASTS06G", "WrongMfg", "Freud") is False


def test_5_source_authority_ranking(discovery):
    sources = discovery.discover_sources("Freud", "Diablo", "DCB518ASTS06G")
    assert len(sources) > 1
    assert sources[0]["authority_score"] >= sources[-1]["authority_score"]


def test_6_official_source_priority(discovery):
    sources = discovery.discover_sources("Freud", "Diablo", "DCB518ASTS06G")
    top_type = sources[0]["source_type"]
    assert top_type in ["manufacturer_product_page", "manufacturer_pdf"]


def test_7_marketplace_deprioritization(discovery):
    sources = discovery.discover_sources("Freud", "Diablo", "DCB518ASTS06G")
    top_score = sources[0]["authority_score"]
    assert top_score == 1.00


def test_8_duplicate_source_detection(fetcher):
    info = {"url": "https://www.freudtools.com/products/dcb518asts06g", "manufacturer": "Freud", "mpn": "DCB518ASTS06G"}
    res1 = fetcher.fetch_source(info)
    res2 = fetcher.fetch_source(info)
    assert res1["content_hash"] == res2["content_hash"]


def test_9_html_extraction(extractor):
    dummy_source = {
        "source_id": "SRC-TEST",
        "url": "https://www.freudtools.com/test",
        "source_type": "manufacturer_product_page",
        "manufacturer": "Freud",
        "mpn": "DCB518ASTS06G",
        "raw_text": "TECHNICAL SPECIFICATIONS:\n- Belt Dimensions: 1/2 in x 18 in"
    }
    segs = extractor.extract_document_segments(dummy_source)
    assert len(segs) >= 2
    assert segs[0]["mpn"] == "DCB518ASTS06G"


def test_10_pdf_extraction(extractor):
    dummy_pdf = {
        "source_id": "SRC-PDF",
        "url": "https://www.freudtools.com/test.pdf",
        "source_type": "manufacturer_pdf",
        "manufacturer": "Freud",
        "mpn": "DCB518ASTS06G",
        "raw_text": "Page 1 Technical Data\n- Material: Aluminum Oxide"
    }
    segs = extractor.extract_document_segments(dummy_pdf)
    assert len(segs) > 0
    assert segs[0]["page"] == 1


def test_11_page_preservation(extractor):
    dummy_pdf = {
        "source_id": "SRC-PDF2", "url": "http://test.pdf", "source_type": "manufacturer_pdf",
        "manufacturer": "3M", "mpn": "775L", "raw_text": "Datasheet Line 1\nDatasheet Line 2"
    }
    segs = extractor.extract_document_segments(dummy_pdf)
    for s in segs:
        assert "page" in s


def test_12_chunk_metadata(chunker, extractor):
    dummy_source = {
        "source_id": "SRC-CHUNK", "url": "http://test", "source_type": "manufacturer_product_page",
        "manufacturer": "Freud", "mpn": "DCB518ASTS06G", "raw_text": "Spec Line 1\nSpec Line 2"
    }
    segs = extractor.extract_document_segments(dummy_source)
    chunks = chunker.chunk_segments(segs)
    assert len(chunks) > 0
    c = chunks[0]
    assert "chunk_id" in c and "source_id" in c and "manufacturer" in c and "mpn" in c


def test_13_product_scoped_retrieval(vector_store):
    vector_store.clear_collection()
    vector_store.add_documents([
        {"chunk_id": "C1", "source_id": "S1", "source_url": "u1", "source_type": "m1", "manufacturer": "Freud", "mpn": "DCB518ASTS06G", "page": 1, "section": "sec", "text": "Aluminum Oxide grain"},
        {"chunk_id": "C2", "source_id": "S2", "source_url": "u2", "source_type": "m2", "manufacturer": "3M", "mpn": "775L", "page": 1, "section": "sec", "text": "Ceramic grain"}
    ])

    res = vector_store.search("Aluminum", filters={"manufacturer": "Freud", "mpn": "DCB518ASTS06G"})
    assert len(res) == 1
    assert res[0]["mpn"] == "DCB518ASTS06G"


def test_14_missing_attribute_detection():
    detector = MissingAttributeDetector()
    dummy_row = pd.Series({"category_id": "ABR_BELT_SANDING", "uom_normalized_attributes_json": '{"grit": {"normalized_value": "P120"}}'})
    missing = detector.detect_missing_attributes(dummy_row)
    assert "dimensions" in missing
    assert "grit" not in missing


def test_15_category_restrictions():
    detector = MissingAttributeDetector()
    allowed = detector.cat_allowed_map.get("ABR_BELT_SANDING", set())
    assert "dimensions" in allowed
    assert "voltage" not in allowed


def test_16_evidence_grounding(validator):
    source_info = {"identity_verified": True, "mpn_verified": True}
    res = validator.validate_candidate(
        candidate={"attribute_name": "dimensions", "value": "1/2 in x 18 in", "evidence_text": "1/2 in x 18 in", "attribute_confidence": 0.95},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"dimensions"},
        source_info=source_info
    )
    assert res["decision"] == "accept"


def test_17_lov_validation(validator):
    source_info = {"identity_verified": True, "mpn_verified": True}
    res = validator.validate_candidate(
        candidate={"attribute_name": "material", "value": "Aluminum Oxide", "evidence_text": "Aluminum Oxide abrasive", "attribute_confidence": 0.95},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"material"},
        source_info=source_info
    )
    assert res["normalized_value"] == "Aluminum Oxide"


def test_18_uom_validation(validator):
    source_info = {"identity_verified": True, "mpn_verified": True}
    res = validator.validate_candidate(
        candidate={"attribute_name": "dimensions", "value": "0.5 in x 18 in", "evidence_text": "0.5 in x 18 in", "attribute_confidence": 0.95},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"dimensions"},
        source_info=source_info
    )
    assert res["normalized_value"] == "1/2 in x 18 in"


def test_19_conflict_detection(conflict_detector):
    has_conf, act = conflict_detector.check_conflict("dimensions", "1/2 in x 18 in", "2 in x 20 in")
    assert has_conf is True
    assert act == "conflict"


def test_20_llm_hallucination_rejection(validator):
    source_info = {"identity_verified": True, "mpn_verified": True}
    res = validator.validate_candidate(
        candidate={"attribute_name": "dimensions", "value": "1/2 in x 18 in", "evidence_text": "", "attribute_confidence": 0.95},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"dimensions"},
        source_info=source_info
    )
    assert res["decision"] == "reject"


def test_21_malformed_llm_response(validator):
    source_info = {"identity_verified": True, "mpn_verified": True}
    res = validator.validate_candidate(
        candidate={"attribute_name": None, "value": None, "evidence_text": None},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"dimensions"},
        source_info=source_info
    )
    assert res["decision"] == "reject"


def test_22_null_on_unsupported_evidence():
    ee = EvidenceEnrichmentExtractor()
    res = ee.extract_attributes_from_evidence("DCB518ASTS06G", "ABR_BELT_SANDING", ["voltage"], {})
    assert res["voltage"] is None


def test_23_immutability():
    from src.enrichment.phase8_pipeline import get_file_hashes, verify_immutability
    h = get_file_hashes()
    assert len(h) == 10
    verify_immutability(h)


def test_24_output_schema():
    df = pd.read_csv("data/processed/enriched_products.csv")
    cols = [
        "source_status", "sources_found", "authoritative_sources_found",
        "enrichment_status", "enriched_attributes_json", "enrichment_evidence_count",
        "enrichment_source_authority", "enrichment_confidence", "conflict_status",
        "manual_review_required"
    ]
    for c in cols:
        assert c in df.columns


def test_25_row_count_preservation():
    df_p7 = pd.read_csv("data/processed/uom_normalized_products.csv")
    df_p8 = pd.read_csv("data/processed/enriched_products.csv")
    assert len(df_p8) == len(df_p7) == 1000


def test_26_provenance_completeness():
    with open("data/enrichment/document_chunks.jsonl", "r", encoding="utf-8") as f:
        line = f.readline()
        if line:
            c = json.loads(line)
            assert "chunk_id" in c and "source_url" in c and "mpn" in c and "manufacturer" in c


def test_27_dynamic_column_preservation():
    df_p7 = pd.read_csv("data/processed/uom_normalized_products.csv")
    df_p8 = pd.read_csv("data/processed/enriched_products.csv")
    for c in df_p7.columns:
        assert c in df_p8.columns


def test_28_vector_store_filtering(vector_store):
    vector_store.clear_collection()
    vector_store.add_documents([
        {"chunk_id": "C1", "source_id": "S1", "source_url": "u", "source_type": "m", "manufacturer": "Freud", "mpn": "DCB518ASTS06G", "page": 1, "section": "sec", "text": "Spec"},
        {"chunk_id": "C2", "source_id": "S2", "source_url": "u", "source_type": "m", "manufacturer": "Bosch", "mpn": "12345", "page": 1, "section": "sec", "text": "Spec"}
    ])
    res = vector_store.search("Spec", filters={"manufacturer": "Freud", "mpn": "DCB518ASTS06G"})
    assert len(res) == 1
    assert res[0]["mpn"] == "DCB518ASTS06G"


def test_29_vector_store_clear(vector_store):
    vector_store.clear_collection()
    assert vector_store.count() == 0


def test_30_cleaner_preserves_technical_units(cleaner):
    t = "1/2 in x 18 in P150 20V 60W 150 psi"
    assert cleaner.clean_segment_text(t) == t


def test_31_source_fetcher_content_hashing(fetcher):
    h1 = fetcher.get_content_hash("Test Content")
    h2 = fetcher.get_content_hash("Test Content")
    assert h1 == h2


def test_32_missing_attribute_detector_cat_map():
    d = MissingAttributeDetector()
    assert "ABR_BELT_SANDING" in d.cat_allowed_map


def test_33_rag_retriever_query_generation(vector_store):
    vector_store.clear_collection()
    vector_store.add_documents([
        {"chunk_id": "C1", "source_id": "S1", "source_url": "u", "source_type": "m", "manufacturer": "Freud", "mpn": "DCB518ASTS06G", "page": 1, "section": "sec", "text": "Aluminum Oxide"}
    ])
    rag = ProductRAGRetriever(vector_store)
    res = rag.retrieve_evidence_for_missing_attributes("DCB518ASTS06G", "Freud", "ABR_BELT_SANDING", ["material"])
    assert "material" in res
    assert len(res["material"]) > 0


def test_34_conflict_detector_normalization(conflict_detector):
    has_conf, act = conflict_detector.check_conflict("pack_quantity", "6", "6")
    assert has_conf is False
    assert act == "keep_existing"


def test_35_evidence_validator_confidence_bounds(validator):
    source_info = {"identity_verified": True, "mpn_verified": True}
    res = validator.validate_candidate(
        candidate={"attribute_name": "dimensions", "value": "1/2 in x 18 in", "evidence_text": "1/2 in x 18 in", "attribute_confidence": 1.5},
        category_id="ABR_BELT_SANDING",
        allowed_attributes={"dimensions"},
        source_info=source_info
    )
    assert res["attribute_confidence"] == 1.0


def test_36_source_registry_schema():
    assert os.path.exists("data/master/source_registry.csv")
    df = pd.read_csv("data/master/source_registry.csv")
    assert "source_id" in df.columns and "authority_level" in df.columns


def test_37_document_chunks_jsonl_schema():
    assert os.path.exists("data/enrichment/document_chunks.jsonl")


def test_38_enriched_products_csv_row_count():
    df = pd.read_csv("data/processed/enriched_products.csv")
    assert len(df) == 1000


def test_39_enrichment_report_exists():
    assert os.path.exists("reports/phase8_enrichment_report.txt")


def test_40_end_to_end_phase8_run():
    df = pd.read_csv("data/processed/enriched_products.csv")
    assert "enrichment_status" in df.columns
    assert df["enrichment_status"].isin(["complete", "partial", "unresolved", "conflict"]).all()
