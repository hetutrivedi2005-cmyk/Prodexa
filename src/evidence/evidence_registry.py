import json
import os
from typing import Dict, List, Optional
from src.evidence.evidence_model import EvidenceRecord


class EvidenceRegistry:
    """
    Component 6 (Phase 9): Evidence Registry Engine.
    Searchable, indexed evidence store supporting fast lookup and deduplication.
    """

    def __init__(self):
        self.records: Dict[str, EvidenceRecord] = {}
        self.by_product: Dict[str, List[EvidenceRecord]] = {}
        self.by_attribute: Dict[str, List[EvidenceRecord]] = {}
        self.by_mpn: Dict[str, List[EvidenceRecord]] = {}
        self.by_source: Dict[str, List[EvidenceRecord]] = {}
        self.by_status: Dict[str, List[EvidenceRecord]] = {}

    def add_record(self, record: EvidenceRecord) -> bool:
        if record.evidence_id in self.records:
            return False  # Duplicate ignored

        self.records[record.evidence_id] = record

        # Indexing
        self.by_product.setdefault(record.product_id, []).append(record)
        self.by_attribute.setdefault(record.attribute_name, []).append(record)
        self.by_mpn.setdefault(record.normalized_mpn, []).append(record)
        self.by_source.setdefault(record.source_id, []).append(record)
        self.by_status.setdefault(record.status, []).append(record)
        return True

    def get_by_id(self, evidence_id: str) -> Optional[EvidenceRecord]:
        return self.records.get(evidence_id)

    def get_by_product(self, product_id: str) -> List[EvidenceRecord]:
        return self.by_product.get(product_id, [])

    def get_by_attribute(self, attribute_name: str) -> List[EvidenceRecord]:
        return self.by_attribute.get(attribute_name, [])

    def get_by_mpn(self, mpn: str) -> List[EvidenceRecord]:
        norm_mpn = str(mpn).strip().upper().replace("-", "").replace(" ", "")
        return self.by_mpn.get(norm_mpn, [])

    def get_by_source(self, source_id: str) -> List[EvidenceRecord]:
        return self.by_source.get(source_id, [])

    def get_verified(self) -> List[EvidenceRecord]:
        return self.by_status.get("verified", [])

    def get_conflicts(self) -> List[EvidenceRecord]:
        return self.by_status.get("conflict", [])

    def count(self) -> int:
        return len(self.records)

    def save_jsonl(self, filepath: str = "data/evidence/evidence_registry.jsonl"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            for rec in self.records.values():
                f.write(json.dumps(rec.to_dict()) + "\n")

    def load_jsonl(self, filepath: str = "data/evidence/evidence_registry.jsonl"):
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                rec = EvidenceRecord(**d)
                self.add_record(rec)
