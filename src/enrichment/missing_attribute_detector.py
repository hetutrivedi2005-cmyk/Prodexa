import os
import json
import pandas as pd
from typing import Dict, List, Set, Any, Optional


class MissingAttributeDetector:
    """
    Component 1: Missing Attribute Detector
    Compares allowed category attributes (from category_attributes.csv) against
    existing validated Phase 7 product attributes to detect missing/incomplete targets.
    """

    def __init__(self, cat_attrs_path: str = "data/master/category_attributes.csv"):
        self.cat_attrs_path = cat_attrs_path
        self.cat_allowed_map: Dict[str, Set[str]] = {}
        self.attr_meta_map: Dict[str, Dict[str, dict]] = {}
        self._load_category_attributes()

    def _load_category_attributes(self):
        if not os.path.exists(self.cat_attrs_path):
            return

        df = pd.read_csv(self.cat_attrs_path)
        for _, row in df.iterrows():
            c_id = str(row["category_id"]).strip()
            a_id = str(row["attribute_id"]).strip()

            if c_id not in self.cat_allowed_map:
                self.cat_allowed_map[c_id] = set()
            self.cat_allowed_map[c_id].add(a_id)

            if c_id not in self.attr_meta_map:
                self.attr_meta_map[c_id] = {}

            self.attr_meta_map[c_id][a_id] = {
                "attribute_name": str(row.get("attribute_name") or a_id).strip(),
                "attribute_type": str(row.get("attribute_type") or "string").strip(),
                "unit_of_measure": str(row.get("unit_of_measure") or "").strip() if pd.notna(row.get("unit_of_measure")) else "",
                "allowed_values": str(row.get("allowed_values") or "").strip() if pd.notna(row.get("allowed_values")) else ""
            }

    def detect_missing_attributes(self, product_row: pd.Series) -> List[str]:
        c_id = str(product_row.get("category_id") or "").strip()
        if not c_id or c_id not in self.cat_allowed_map:
            return []

        allowed_attrs = self.cat_allowed_map[c_id]

        # Extract existing attribute names from Phase 7 JSON
        existing_attrs = set()
        for json_col in ["uom_normalized_attributes_json", "lov_resolved_attributes_json", "extracted_attributes_json"]:
            raw_json = str(product_row.get(json_col) or "").strip()
            if raw_json and raw_json != "{}":
                try:
                    parsed = json.loads(raw_json)
                    for k, v in parsed.items():
                        # Check if value is present and non-empty
                        if isinstance(v, dict):
                            val = v.get("normalized_value") or v.get("canonical_value") or v.get("value")
                        else:
                            val = v

                        if val is not None and str(val).strip() not in ["", "None", "null"]:
                            existing_attrs.add(k)
                except Exception:
                    pass

        # Identify missing attributes
        missing = [a for a in sorted(list(allowed_attrs)) if a not in existing_attrs]
        return missing

    def get_attribute_metadata(self, category_id: str, attribute_id: str) -> Optional[dict]:
        return self.attr_meta_map.get(category_id, {}).get(attribute_id)
