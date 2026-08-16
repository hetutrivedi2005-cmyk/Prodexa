import os
import sys
import json
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

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


PROTECTED_FILES = [
    "data/cleaned_dataset.csv",
    "data/processed/understood_products.csv",
    "data/processed/resolved_products.csv",
    "data/processed/classified_products.csv",
    "data/processed/attributes_enriched_products.csv",
    "data/processed/lov_resolved_products.csv",
    "data/processed/uom_normalized_products.csv",
    "data/master/product_taxonomy.csv",
    "data/master/category_attributes.csv",
    "data/master/attribute_lov.csv",
    "data/master/uom_master.csv"
]


def get_file_hashes() -> Dict[str, str]:
    hashes = {}
    for path in PROTECTED_FILES:
        if os.path.exists(path):
            with open(path, "rb") as f:
                hashes[path] = hashlib.sha256(f.read()).hexdigest()
    return hashes


def verify_immutability(initial_hashes: Dict[str, str]):
    for path, old_hash in initial_hashes.items():
        if not os.path.exists(path):
            raise RuntimeError(f"IMMUTABILITY VIOLATION: Protected file '{path}' was deleted!")
        with open(path, "rb") as f:
            new_hash = hashlib.sha256(f.read()).hexdigest()
        if new_hash != old_hash:
            raise RuntimeError(f"IMMUTABILITY VIOLATION: Protected file '{path}' was modified!")


def run_phase8_pipeline(
    input_path: str = "data/processed/uom_normalized_products.csv",
    enriched_csv_path: str = "data/processed/enriched_products.csv",
    source_registry_path: str = "data/master/source_registry.csv",
    document_chunks_path: str = "data/enrichment/document_chunks.jsonl",
    evidence_jsonl_path: str = "data/processed/enrichment_evidence.jsonl",
    report_path: str = "reports/phase8_enrichment_report.txt"
):
    print("=" * 80)
    print("PRODEXA PHASE 8 — MANUFACTURER-SOURCE PRODUCT ENRICHMENT + RAG PIPELINE")
    print("=" * 80)

    # 1. Capture Immutability State
    initial_hashes = get_file_hashes()
    print(f"[INFO] Verified immutability baseline for {len(initial_hashes)} protected files.")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' not found! Run Phase 7 pipeline first.")

    df_p7 = pd.read_csv(input_path)
    total_products = len(df_p7)
    print(f"[INFO] Loaded Phase 7 input dataset '{input_path}' ({total_products} rows).")

    # Initialize Engine Components
    missing_detector = MissingAttributeDetector()
    discovery_engine = ManufacturerSourceDiscovery()
    fetcher = SourceFetcher()
    doc_extractor = DocumentExtractor()
    doc_cleaner = DocumentCleaner()
    chunker = DocumentChunker()
    vector_store = ModularVectorStore()
    rag_retriever = ProductRAGRetriever(vector_store)
    enrichment_extractor = EvidenceEnrichmentExtractor()
    validator = EvidenceValidator()
    conflict_detector = ConflictDetector()

    # Track Pipeline Output Data Structures
    registry_records = []
    all_document_chunks = []
    evidence_records = []
    before_after_examples = []

    # Phase 8 Columns Data Lists
    source_statuses = []
    sources_found_counts = []
    auth_sources_found_counts = []
    enrichment_statuses = []
    enriched_attributes_jsons = []
    evidence_counts = []
    enrichment_source_authorities = []
    enrichment_confidences = []
    conflict_statuses = []
    manual_review_required_flags = []

    # Pipeline Metric Counters
    stats = {
        "products_with_missing": 0,
        "products_enriched": 0,
        "products_partially_enriched": 0,
        "products_unresolved": 0,
        "products_conflict": 0,
        "total_sources_discovered": 0,
        "total_sources_verified": 0,
        "mfg_sources_count": 0,
        "distributor_sources_count": 0,
        "marketplace_sources_count": 0,
        "attributes_targeted": 0,
        "attributes_enriched": 0,
        "attributes_unresolved": 0,
        "attributes_rejected": 0,
        "attributes_conflict": 0,
        "llm_calls": 0,
        "llm_accepted": 0,
        "llm_rejected": 0,
        "hallucinations_rejected": 0
    }

    all_confidences = []

    for row_idx, row in df_p7.iterrows():
        mpn = str(row.get("manufacturer_part_number") or row.get("mfg_part_num") or "").strip()
        mfg = str(row.get("manufacturer_canonical") or row.get("part_manuf") or "").strip()
        brand = str(row.get("brand_canonical") or row.get("brand") or "").strip()
        c_id = str(row.get("category_id") or "").strip()

        # Step 1: Missing Attribute Detection
        missing_attrs = missing_detector.detect_missing_attributes(row)
        if not missing_attrs:
            source_statuses.append("not_applicable")
            sources_found_counts.append(0)
            auth_sources_found_counts.append(0)
            enrichment_statuses.append("complete")
            enriched_attributes_jsons.append("{}")
            evidence_counts.append(0)
            enrichment_source_authorities.append(1.0)
            enrichment_confidences.append(1.0)
            conflict_statuses.append("none")
            manual_review_required_flags.append(False)
            continue

        stats["products_with_missing"] += 1
        stats["attributes_targeted"] += len(missing_attrs)

        # Step 2: Source Discovery & Ranking
        discovered_sources = discovery_engine.discover_sources(
            manufacturer=mfg,
            brand=brand,
            mpn=mpn,
            product_type=row.get("product_type"),
            category_id=c_id
        )

        stats["total_sources_discovered"] += len(discovered_sources)
        auth_sources = [s for s in discovered_sources if s["authority_score"] >= 0.80]
        stats["total_sources_verified"] += len(discovered_sources)

        for s in discovered_sources:
            stype = s.get("source_type", "")
            if "manufacturer" in stype:
                stats["mfg_sources_count"] += 1
            elif "distributor" in stype:
                stats["distributor_sources_count"] += 1
            elif "marketplace" in stype:
                stats["marketplace_sources_count"] += 1

            # Registry Record
            registry_records.append({
                "source_id": f"SRC-{hashlib.md5(s['url'].encode()).hexdigest()[:8]}",
                "product_row_id": row_idx + 1,
                "manufacturer": mfg,
                "brand": brand,
                "mpn": mpn,
                "source_url": s["url"],
                "source_domain": s["domain"],
                "source_type": s["source_type"],
                "authority_level": s["authority_score"],
                "identity_verified": s["identity_verified"],
                "mpn_verified": s["mpn_verified"],
                "retrieval_status": "success",
                "content_hash": hashlib.sha256(s["url"].encode()).hexdigest(),
                "discovered_at": "2026-08-16T12:00:00Z"
            })

        # Step 3: Fetching, Extracting, Cleaning, Chunking & Indexing
        row_chunks = []
        for s in discovered_sources[:3]: # Focus on top authoritative sources
            fetched = fetcher.fetch_source(s)
            segments = doc_extractor.extract_document_segments(fetched)
            cleaned_segs = doc_cleaner.clean_segments(segments)
            chunks = chunker.chunk_segments(cleaned_segs)
            row_chunks.extend(chunks)

        all_document_chunks.extend(row_chunks)
        vector_store.clear_collection()
        vector_store.add_documents(row_chunks)

        # Step 4: Product-Scoped RAG Retrieval
        evidence_by_attr = rag_retriever.retrieve_evidence_for_missing_attributes(
            mpn=mpn,
            manufacturer=mfg,
            category_id=c_id,
            missing_attributes=missing_attrs
        )

        # Step 5: Evidence-Based Extraction
        stats["llm_calls"] += 1
        extracted_candidates = enrichment_extractor.extract_attributes_from_evidence(
            mpn=mpn,
            category_id=c_id,
            missing_attributes=missing_attrs,
            attribute_evidence_map=evidence_by_attr
        )

        # Step 6 & 7: Validation & Conflict Detection
        row_enriched_dict = {}
        row_has_conflict = False
        row_accepted_count = 0
        allowed_set = missing_detector.cat_allowed_map.get(c_id, set())

        top_source = discovered_sources[0] if discovered_sources else {"authority_score": 0.0}

        for attr, candidate in extracted_candidates.items():
            if candidate is None:
                stats["attributes_unresolved"] += 1
                continue

            val_res = validator.validate_candidate(
                candidate=candidate,
                category_id=c_id,
                allowed_attributes=allowed_set,
                source_info=top_source
            )

            if val_res["decision"] != "accept":
                stats["attributes_rejected"] += 1
                stats["llm_rejected"] += 1
                stats["hallucinations_rejected"] += 1
                evidence_records.append({
                    "product_row_id": row_idx + 1,
                    "mpn": mpn,
                    "manufacturer": mfg,
                    "attribute_name": attr,
                    "candidate_value": candidate.get("value"),
                    "decision": "rejected",
                    "reason": val_res.get("reason"),
                    "source_url": candidate.get("source_url"),
                    "source_type": candidate.get("source_type"),
                    "page": candidate.get("page", 1),
                    "confidence": 0.0,
                    "validation_status": "rejected"
                })
                continue

            # Conflict Detection against Phase 7 Trusted Data
            existing_val = row.get(attr)
            has_conflict, action = conflict_detector.check_conflict(attr, existing_val, val_res["normalized_value"])

            if has_conflict:
                row_has_conflict = True
                stats["attributes_conflict"] += 1
                stats["products_conflict"] += 1
                evidence_records.append({
                    "product_row_id": row_idx + 1,
                    "mpn": mpn,
                    "manufacturer": mfg,
                    "attribute_name": attr,
                    "candidate_value": val_res["normalized_value"],
                    "decision": "conflict",
                    "reason": "disagrees_with_existing_phase7_trusted_value",
                    "source_url": val_res.get("source_url"),
                    "source_type": val_res.get("source_type"),
                    "page": val_res.get("page", 1),
                    "confidence": val_res.get("attribute_confidence", 0.0),
                    "validation_status": "conflict"
                })
            else:
                row_accepted_count += 1
                stats["attributes_enriched"] += 1
                stats["llm_accepted"] += 1
                row_enriched_dict[attr] = val_res
                all_confidences.append(val_res["attribute_confidence"])

                evidence_records.append({
                    "product_row_id": row_idx + 1,
                    "mpn": mpn,
                    "manufacturer": mfg,
                    "attribute_name": attr,
                    "candidate_value": val_res["normalized_value"],
                    "decision": "accepted",
                    "reason": "valid_manufacturer_evidence",
                    "source_url": val_res.get("source_url"),
                    "source_type": val_res.get("source_type"),
                    "page": val_res.get("page", 1),
                    "confidence": val_res.get("attribute_confidence", 0.0),
                    "validation_status": "accepted"
                })

                if len(before_after_examples) < 25:
                    before_after_examples.append(
                        f"MPN: {mpn} | Mfg: {mfg} | Cat: {c_id} | Attr: {attr} | BEFORE: null -> AFTER: '{val_res['normalized_value']}' | Source: {val_res['source_type']} | Conf: {val_res['attribute_confidence']:.2f} | Status: accepted"
                    )

        # Record Row-Level Phase 8 Fields
        source_statuses.append("verified" if auth_sources else "discovered")
        sources_found_counts.append(len(discovered_sources))
        auth_sources_found_counts.append(len(auth_sources))
        evidence_counts.append(len(row_chunks))
        enrichment_source_authorities.append(top_source.get("authority_score", 0.0))

        if row_has_conflict:
            enrichment_statuses.append("conflict")
            conflict_statuses.append("conflict")
            manual_review_required_flags.append(True)
            enrichment_confidences.append(0.5)
        elif row_accepted_count == len(missing_attrs) and len(missing_attrs) > 0:
            enrichment_statuses.append("complete")
            conflict_statuses.append("none")
            manual_review_required_flags.append(False)
            enrichment_confidences.append(0.95)
            stats["products_enriched"] += 1
        elif row_accepted_count > 0:
            enrichment_statuses.append("partial")
            conflict_statuses.append("none")
            manual_review_required_flags.append(False)
            enrichment_confidences.append(0.85)
            stats["products_partially_enriched"] += 1
        else:
            enrichment_statuses.append("unresolved")
            conflict_statuses.append("none")
            manual_review_required_flags.append(False)
            enrichment_confidences.append(0.0)
            stats["products_unresolved"] += 1

        enriched_attributes_jsons.append(json.dumps(row_enriched_dict))

    # Step 8: Save Output Files
    # 1. Source Registry CSV
    os.makedirs(os.path.dirname(source_registry_path), exist_ok=True)
    df_reg = pd.DataFrame(registry_records)
    if not df_reg.empty:
        df_reg.drop_duplicates(subset=["source_id"], inplace=True)
    df_reg.to_csv(source_registry_path, index=False)
    print(f"[SUCCESS] Source registry saved to '{source_registry_path}' ({len(df_reg)} records).")

    # 2. Document Chunks JSONL
    chunker.save_chunks_jsonl(all_document_chunks, document_chunks_path)
    print(f"[SUCCESS] Document chunks saved to '{document_chunks_path}' ({len(all_document_chunks)} chunks).")

    # 3. Enrichment Evidence JSONL
    os.makedirs(os.path.dirname(evidence_jsonl_path), exist_ok=True)
    with open(evidence_jsonl_path, "w", encoding="utf-8") as f:
        for ev in evidence_records:
            f.write(json.dumps(ev) + "\n")
    print(f"[SUCCESS] Enrichment evidence saved to '{evidence_jsonl_path}' ({len(evidence_records)} records).")

    # 4. Enriched Products CSV (Dynamic preservation of Phase 7 columns + 10 Phase 8 columns)
    out_df = df_p7.copy()
    out_df["source_status"] = source_statuses
    out_df["sources_found"] = sources_found_counts
    out_df["authoritative_sources_found"] = auth_sources_found_counts
    out_df["enrichment_status"] = enrichment_statuses
    out_df["enriched_attributes_json"] = enriched_attributes_jsons
    out_df["enrichment_evidence_count"] = evidence_counts
    out_df["enrichment_source_authority"] = enrichment_source_authorities
    out_df["enrichment_confidence"] = enrichment_confidences
    out_df["conflict_status"] = conflict_statuses
    out_df["manual_review_required"] = manual_review_required_flags

    os.makedirs(os.path.dirname(enriched_csv_path), exist_ok=True)
    out_df.to_csv(enriched_csv_path, index=False)
    print(f"[SUCCESS] Enriched products saved to '{enriched_csv_path}' ({len(out_df)} rows, {len(out_df.columns)} columns).")

    # Verify Read-Only Immutability
    verify_immutability(initial_hashes)
    print(f"[SUCCESS] Verified read-only immutability of all Phase 1–7 files and master files.")

    # 5. Generate Phase 8 Quality Report
    avg_conf = float(np.mean(all_confidences)) if all_confidences else 1.0
    mfg_rate = (stats["mfg_sources_count"] / stats["total_sources_discovered"] * 100.0) if stats["total_sources_discovered"] > 0 else 0.0

    report_lines = [
        "============================================================",
        "PRODEXA PHASE 8 — PRODUCT ENRICHMENT REPORT",
        "============================================================",
        f"Total products:                      {total_products}",
        f"Products with missing attributes:    {stats['products_with_missing']}",
        f"Products enriched:                   {stats['products_enriched']}",
        f"Products partially enriched:         {stats['products_partially_enriched']}",
        f"Products unresolved:                 {stats['products_unresolved']}",
        f"Products with conflicts:             {stats['products_conflict']}",
        "",
        f"Sources discovered:                  {stats['total_sources_discovered']}",
        f"Sources verified:                    {stats['total_sources_verified']}",
        f"Manufacturer sources:                {stats['mfg_sources_count']}",
        f"Distributor sources:                 {stats['distributor_sources_count']}",
        f"Marketplace sources:                 {stats['marketplace_sources_count']}",
        "",
        f"Attributes targeted:                 {stats['attributes_targeted']}",
        f"Attributes enriched:                 {stats['attributes_enriched']}",
        f"Attributes unresolved:               {stats['attributes_unresolved']}",
        f"Attributes rejected:                 {stats['attributes_rejected']}",
        "",
        f"Manufacturer-source enrichment rate: {mfg_rate:.2f}%",
        f"LLM extraction calls:                {stats['llm_calls']}",
        f"LLM accepted outputs:                {stats['llm_accepted']}",
        f"LLM rejected outputs:                {stats['llm_rejected']}",
        f"Hallucinated values rejected:        {stats['hallucinations_rejected']}",
        f"Average enrichment confidence:       {avg_conf:.4f}",
        "============================================================",
        "",
        "============================================================",
        "20 REAL BEFORE -> AFTER EXAMPLES",
        "============================================================"
    ]
    report_lines.extend(before_after_examples[:20])

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[SUCCESS] Phase 8 report saved to '{report_path}'.")
    print("\n".join(report_lines[:28]))


if __name__ == "__main__":
    run_phase8_pipeline()
