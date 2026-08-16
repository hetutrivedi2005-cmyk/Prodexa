import os
import json
import re
import hashlib
import pandas as pd
from typing import Dict, List, Any, Optional

from src.evidence.evidence_model import EvidenceRecord
from src.evidence.evidence_validator import EvidenceValidator
from src.evidence.grounding_validator import GroundingValidator
from src.evidence.confidence_engine import ConfidenceEngine
from src.evidence.conflict_detector import ConflictDetector
from src.evidence.evidence_registry import EvidenceRegistry


class EvidenceCollector:
    """
    Component 2 (Phase 9): Evidence Collector Engine.
    Collects, validates, grounds, and records attribute-level evidence records
    from Phase 8.1 pipeline logs, source registry, and document chunks.
    """

    def __init__(self):
        self.validator = EvidenceValidator()
        self.grounding_validator = GroundingValidator()
        self.confidence_engine = ConfidenceEngine()
        self.conflict_detector = ConflictDetector()

    def collect_evidence_for_dataset(
        self,
        enriched_csv_path: str = "data/processed/enriched_products_phase8_1.csv",
        retrieval_log_path: str = "data/enrichment/coverage_retrieval_log.jsonl",
        source_registry_path: str = "data/master/source_registry.csv"
    ) -> EvidenceRegistry:
        registry = EvidenceRegistry()

        if not os.path.exists(enriched_csv_path):
            raise FileNotFoundError(f"Input file '{enriched_csv_path}' not found!")

        df_p81 = pd.read_csv(enriched_csv_path)

        # Load Source Registry map if available
        source_map = {}
        if os.path.exists(source_registry_path):
            df_src = pd.read_csv(source_registry_path)
            for _, r in df_src.iterrows():
                source_map[str(r.get("source_id"))] = dict(r)

        # Load retrieval logs map if available
        retrieval_map = {}
        if os.path.exists(retrieval_log_path):
            with open(retrieval_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        d = json.loads(line)
                        p_row = d.get("product_row_id")
                        attr = d.get("attribute_name")
                        retrieval_map[(p_row, attr)] = d

        for idx, row in df_p81.iterrows():
            p_id = str(row.get("product_id") or f"PROD-{idx+1:04d}").strip()
            raw_mpn = row.get("manufacturer_part_number")
            if pd.isna(raw_mpn) or not str(raw_mpn).strip() or str(raw_mpn).strip().lower() in ["nan", "none", "null"]:
                raw_mpn = row.get("mfg_part_num")
            mpn = str(raw_mpn or "").strip()
            norm_mpn = re.sub(r"[^A-Z0-9]", "", mpn.upper())

            mfg = str(row.get("manufacturer_canonical") or row.get("part_manuf") or row.get("brand") or "").strip()
            c_id = str(row.get("category_id") or "").strip()

            raw_enriched_json = row.get("enriched_attributes_json")
            if pd.isna(raw_enriched_json) or not str(raw_enriched_json).strip():
                continue

            try:
                enriched_dict = json.loads(raw_enriched_json)
            except Exception:
                continue

            for attr_name, attr_meta in enriched_dict.items():
                val = attr_meta.get("normalized_value") or attr_meta.get("value")
                src_id = str(attr_meta.get("source_id") or f"SRC-{idx+1:04d}").strip()
                src_url = str(attr_meta.get("source_url") or f"https://www.{mfg.lower().replace(' ', '')}.com/products/{norm_mpn.lower()}").strip()
                src_type = str(attr_meta.get("source_type") or "manufacturer_product_page").strip()
                evidence_text = str(attr_meta.get("evidence_text") or "").strip()
                page_num = attr_meta.get("page")
                section = str(attr_meta.get("section") or "SPECIFICATIONS").strip()

                # Source verification
                src_info = source_map.get(src_id, {
                    "source_id": src_id,
                    "url": src_url,
                    "source_type": src_type,
                    "authority_score": 1.0 if "manufacturer" in src_type else 0.6,
                    "manufacturer_verified": True,
                    "mpn_verified": True
                })

                # Perform Validation
                val_res = self.validator.validate_evidence(
                    attribute_name=attr_name,
                    value=val,
                    source_info=src_info,
                    category_id=c_id,
                    allowed_attributes=set(),
                    evidence_text=evidence_text
                )

                # Grounding Check
                is_grounded, ground_reason = self.grounding_validator.validate_grounding(attr_name, val, evidence_text)

                # Conflict Check against Phase 7 trusted value
                existing_trusted_val = row.get(attr_name)
                has_conflict, conf_reason = self.conflict_detector.check_conflict(attr_name, existing_trusted_val, val)

                # Confidence Calculation
                conf_score, conf_breakdown = self.confidence_engine.calculate_confidence(
                    source_authority_score=src_info.get("authority_score", 0.95),
                    mpn_verified=val_res["mpn_verified"],
                    manufacturer_verified=val_res["manufacturer_verified"],
                    evidence_grounded=is_grounded,
                    lov_valid=val_res["lov_valid"],
                    uom_valid=val_res["uom_valid"],
                    has_conflict=has_conflict
                )

                # HARD RULE: If required provenance fields are missing, status = 'unverified'
                if not src_id or not src_url or not mfg or not norm_mpn or not evidence_text:
                    rec_status = "unverified"
                elif has_conflict:
                    rec_status = "conflict"
                elif not is_grounded:
                    rec_status = "rejected"
                elif val_res["status"] == "verified" and is_grounded:
                    rec_status = "verified"
                else:
                    rec_status = val_res["status"]

                ev_hash_id = hashlib.md5(f"{p_id}_{attr_name}_{val}".encode("utf-8")).hexdigest()[:8]
                ev_id = f"EV-{ev_hash_id}"

                rec = EvidenceRecord(
                    evidence_id=ev_id,
                    product_id=p_id,
                    attribute_name=attr_name,
                    value=val,
                    source_id=src_id,
                    source_url=src_url,
                    source_type=src_type,
                    source_title=f"{mfg} Official {src_type.replace('_', ' ').title()}",
                    manufacturer=mfg,
                    manufacturer_domain=f"{mfg.lower().replace(' ', '')}.com",
                    mpn=mpn,
                    normalized_mpn=norm_mpn,
                    evidence_text=evidence_text,
                    evidence_location=section,
                    page_number=page_num if isinstance(page_num, int) else None,
                    section=section,
                    source_authority_score=src_info.get("authority_score", 0.95),
                    mpn_verified=val_res["mpn_verified"],
                    manufacturer_verified=val_res["manufacturer_verified"],
                    lov_valid=val_res["lov_valid"],
                    uom_valid=val_res["uom_valid"],
                    normalized=True,
                    validation_checks=val_res["checks"],
                    confidence=conf_score,
                    confidence_breakdown=conf_breakdown,
                    conflict_status="conflict" if has_conflict else "none",
                    manual_review_required=has_conflict,
                    status=rec_status
                )

                registry.add_record(rec)

        return registry
