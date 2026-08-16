import os
import json
import pytest
import pandas as pd

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
from src.enrichment.phase8_1_pipeline import get_clean_mpn, get_clean_mfg, get_file_hashes, verify_immutability


@pytest.fixture(scope="module")
def discovery():
    return ManufacturerSourceDiscovery()


@pytest.fixture(scope="module")
def fetcher():
    return SourceFetcher()


@pytest.fixture(scope="module")
def extractor():
    return EvidenceEnrichmentExtractor()


@pytest.fixture(scope="module")
def cleaner():
    return DocumentCleaner()


@pytest.fixture(scope="module")
def chunker():
    return DocumentChunker()


@pytest.fixture(scope="module")
def vector_store():
    return ModularVectorStore()


def test_1_generate_search_queries(discovery):
    queries = discovery.generate_search_queries("DCB518ASTS06G", "Freud", "Sanding Belt", "dimensions")
    assert len(queries) >= 8
    assert "DCB518ASTS06G dimensions" in queries


def test_2_domain_discovery_reusable(discovery):
    d1 = discovery._discover_manufacturer_domain("Freud", "Diablo")
    d2 = discovery._discover_manufacturer_domain("3M Co", "3M")
    assert "freud" in d1
    assert "3m" in d2


def test_3_source_verification_details(discovery):
    srcs = discovery.discover_sources("Freud", "Diablo", "DCB518ASTS06G")
    top = srcs[0]
    assert top["source_discovered"] is True
    assert top["manufacturer_verified"] is True
    assert top["mpn_verified"] is True
    assert top["verification_status"] == "verified"


def test_4_clean_mpn_helper():
    s1 = pd.Series({"manufacturer_part_number": None, "mfg_part_num": "DCB518ASTS06G"})
    assert get_clean_mpn(s1) == "DCB518ASTS06G"


def test_5_clean_mfg_helper():
    s1 = pd.Series({"manufacturer_canonical": None, "part_manuf": "Freud Inc"})
    assert get_clean_mfg(s1) == "Freud Inc"


def test_6_synonym_query_expansion(vector_store):
    rag = ProductRAGRetriever(vector_store)
    syns = rag.ATTRIBUTE_SYNONYMS.get("dimensions")
    assert "length" in syns and "width" in syns


def test_7_evidence_scoring_exact_mpn(vector_store):
    rag = ProductRAGRetriever(vector_store)
    chunk = {"text": "DCB518ASTS06G Dimensions: 1/2 in x 18 in", "mpn": "DCB518ASTS06G", "source_type": "manufacturer_pdf", "section": "SPECIFICATIONS"}
    score = rag._calculate_evidence_score(chunk, "DCB518ASTS06G", "dimensions", ["dimensions", "size"])
    assert score >= 0.70


def test_8_evidence_scoring_threshold(vector_store):
    rag = ProductRAGRetriever(vector_store)
    chunk = {"text": "Unrelated text", "mpn": "WRONG", "source_type": "marketplace", "section": "GENERAL"}
    score = rag._calculate_evidence_score(chunk, "DCB518ASTS06G", "dimensions", ["dimensions"])
    assert score < 0.50


def test_9_section_aware_chunking(chunker):
    segs = [{"source_id": "S1", "source_url": "u", "source_type": "m", "manufacturer": "Freud", "mpn": "DCB518ASTS06G", "page": 1, "section": "TECHNICAL SPECIFICATIONS", "text": "Spec 1"}]
    chunks = chunker.chunk_segments(segs)
    assert len(chunks) == 1
    assert chunks[0]["section"] == "TECHNICAL SPECIFICATIONS"


def test_10_cleaner_header_stripping(cleaner):
    t = "Page 1 of 5\nSPECIFICATIONS:\n- Dimensions: 1/2 in x 18 in"
    cleaned = cleaner.clean_segment_text(t)
    assert "Page 1 of 5" not in cleaned
    assert "Dimensions" in cleaned


def test_11_extractor_length_extraction(extractor):
    v = extractor._extract_value_from_text("length", "Board Length: 12 ft")
    assert v == "12 ft"


def test_12_extractor_width_profile_extraction(extractor):
    v = extractor._extract_value_from_text("width_profile", "Width Profile: 1x6")
    assert v == "1x6"


def test_13_extractor_color_extraction(extractor):
    v = extractor._extract_value_from_text("color", "Color Tone: Slate Gray")
    assert v == "Slate Gray"


def test_14_extractor_edge_profile_extraction(extractor):
    v = extractor._extract_value_from_text("edge_profile", "Edge Profile: Grooved")
    assert v == "Grooved"


def test_15_extractor_wattage_extraction(extractor):
    v = extractor._extract_value_from_text("wattage", "Wattage Rating: 60W")
    assert v == "60W"


def test_16_extractor_color_temperature_extraction(extractor):
    v = extractor._extract_value_from_text("color_temperature", "Color Temperature: 2700K Warm White")
    assert v == "2700K"


def test_17_extractor_power_type_extraction(extractor):
    v = extractor._extract_value_from_text("power_type", "Power Source: Electric")
    assert v == "Electric"


def test_18_extractor_drive_size_extraction(extractor):
    v = extractor._extract_value_from_text("drive_size", "Drive Size: 1/4 in Hex")
    assert v == "1/4 in"


def test_19_immutability_verification():
    h = get_file_hashes()
    assert len(h) == 10
    verify_immutability(h)


def test_20_coverage_retrieval_log_exists():
    assert os.path.exists("data/enrichment/coverage_retrieval_log.jsonl")


def test_21_phase8_1_enriched_products_csv_row_count():
    assert os.path.exists("data/processed/enriched_products_phase8_1.csv")
    df = pd.read_csv("data/processed/enriched_products_phase8_1.csv")
    assert len(df) == 1000


def test_22_phase8_1_coverage_report_exists():
    assert os.path.exists("reports/phase8_1_coverage_report.txt")


def test_23_phase8_1_adversarial_audit_report_exists():
    assert os.path.exists("reports/phase8_1_adversarial_audit.txt")


def test_24_dynamic_column_preservation_phase8_1():
    df_p7 = pd.read_csv("data/processed/uom_normalized_products.csv")
    df_p81 = pd.read_csv("data/processed/enriched_products_phase8_1.csv")
    for c in df_p7.columns:
        assert c in df_p81.columns


def test_25_end_to_end_coverage_increase():
    df = pd.read_csv("data/processed/enriched_products_phase8_1.csv")
    enriched_rows = df[df["enrichment_status"].isin(["complete", "partial"])]
    assert len(enriched_rows) >= 200
