import hashlib
import re
from typing import List, Dict, Any, Tuple


class EvidenceDeduplicator:
    """
    Component 4 (Phase 9.1): Evidence Deduplication Engine.
    Identifies and merges duplicate evidence records across HTML, PDF, and cached documents.
    """

    def deduplicate_records(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        seen_keys = set()
        seen_sources = set()
        unique_records = []
        duplicate_records_count = 0
        duplicate_sources_count = 0

        for r in records:
            url = str(r.get("source_url") or "").strip().lower()
            mpn = str(r.get("normalized_mpn") or r.get("mpn") or "").strip().upper().replace("-", "")
            attr = str(r.get("attribute_name") or "").strip().lower()
            val = str(r.get("value") or "").strip().lower()
            ev_text = str(r.get("evidence_text") or "").strip().lower()

            ev_hash = hashlib.md5(ev_text.encode("utf-8")).hexdigest()[:10]
            comp_key = f"{url}|{mpn}|{attr}|{val}|{ev_hash}"

            source_key = f"{url}|{mpn}"
            if source_key in seen_sources:
                duplicate_sources_count += 1
            else:
                seen_sources.add(source_key)

            if comp_key in seen_keys:
                duplicate_records_count += 1
                continue

            seen_keys.add(comp_key)
            unique_records.append(r)

        stats = {
            "total_input_records": len(records),
            "unique_evidence_count": len(unique_records),
            "duplicate_evidence_removed": duplicate_records_count,
            "duplicate_sources_removed": duplicate_sources_count
        }

        return unique_records, stats
