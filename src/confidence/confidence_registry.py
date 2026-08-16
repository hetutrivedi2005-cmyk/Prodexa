import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from src.confidence.confidence_model import AttributeConfidence


class ConfidenceRegistry:
    """
    Component 4 (Phase 11): Confidence Registry Store.
    Indexed in-memory and persistent store for attribute-level confidence records.
    """

    def __init__(self):
        self._records: List[AttributeConfidence] = []
        self._by_product: Dict[str, List[AttributeConfidence]] = {}
        self._by_key: Dict[Tuple[str, str], AttributeConfidence] = {}

    def add_record(self, record: AttributeConfidence):
        self._records.append(record)
        self._by_product.setdefault(record.product_id, []).append(record)
        self._by_key[(record.product_id, record.attribute_name)] = record

    def get_by_product(self, product_id: str) -> List[AttributeConfidence]:
        return self._by_product.get(product_id, [])

    def get_by_key(self, product_id: str, attribute_name: str) -> Optional[AttributeConfidence]:
        return self._by_key.get((product_id, attribute_name))

    def get_all(self) -> List[AttributeConfidence]:
        return self._records

    def save_jsonl(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            for r in self._records:
                f.write(json.dumps(r.to_dict()) + "\n")

    def save_csv(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        rows = []
        for r in self._records:
            d = r.to_dict()
            d["reason_codes"] = "|".join(r.reason_codes)
            rows.append(d)
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
