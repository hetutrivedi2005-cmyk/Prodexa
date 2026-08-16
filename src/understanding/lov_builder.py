import os
import re
import json
import pandas as pd
from typing import Dict, List, Set, Any, Optional, Tuple


class LOVBuilder:
    """
    Part 1 — Attribute LOV & UOM Master Builder
    Derives canonical attribute LOV master (attribute_lov.csv) and UOM master (uom_master.csv)
    directly from actual observed Phase 5 attribute data in attributes_enriched_products.csv
    and controlled category_attributes.csv.
    """

    def __init__(
        self,
        enriched_csv_path: str = "data/processed/attributes_enriched_products.csv",
        cat_attrs_csv_path: str = "data/master/category_attributes.csv",
        lov_output_path: str = "data/master/attribute_lov.csv",
        uom_output_path: str = "data/master/uom_master.csv"
    ):
        self.enriched_csv_path = enriched_csv_path
        self.cat_attrs_csv_path = cat_attrs_csv_path
        self.lov_output_path = lov_output_path
        self.uom_output_path = uom_output_path

    def build_masters(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        # 1. Build UOM Master (uom_master.csv)
        uom_rows = [
            {"uom_id": "UOM_IN", "canonical_uom": "in", "normalized_uom": "in", "aliases": "IN;INCH;INCHES;\"", "dimension_type": "length", "is_active": True},
            {"uom_id": "UOM_MM", "canonical_uom": "mm", "normalized_uom": "mm", "aliases": "MM;MILLIMETER;MILLIMETERS;M.M.", "dimension_type": "length", "is_active": True},
            {"uom_id": "UOM_FT", "canonical_uom": "ft", "normalized_uom": "ft", "aliases": "FT;FEET;FOOT;'", "dimension_type": "length", "is_active": True},
            {"uom_id": "UOM_V", "canonical_uom": "V", "normalized_uom": "v", "aliases": "VOLT;VOLTS;V;v", "dimension_type": "electrical", "is_active": True},
            {"uom_id": "UOM_W", "canonical_uom": "W", "normalized_uom": "w", "aliases": "WATT;WATTS;W;w", "dimension_type": "power", "is_active": True},
            {"uom_id": "UOM_AH", "canonical_uom": "Ah", "normalized_uom": "ah", "aliases": "AH;AMP HOUR;AMP-HOUR", "dimension_type": "capacity", "is_active": True},
            {"uom_id": "UOM_K", "canonical_uom": "K", "normalized_uom": "k", "aliases": "KELVIN;K;k", "dimension_type": "temperature", "is_active": True},
            {"uom_id": "UOM_PC", "canonical_uom": "pcs", "normalized_uom": "pcs", "aliases": "PC;PCS;PIECE;PIECES;PK;PACK;BOX", "dimension_type": "count", "is_active": True},
            {"uom_id": "UOM_GRIT", "canonical_uom": "Grit", "normalized_uom": "grit", "aliases": "GRIT;P-GRIT", "dimension_type": "coarseness", "is_active": True}
        ]
        uom_df = pd.DataFrame(uom_rows)
        os.makedirs(os.path.dirname(self.uom_output_path), exist_ok=True)
        uom_df.to_csv(self.uom_output_path, index=False)

        # Standard known alias dictionary (semantic word/material abbreviations)
        known_aliases = {
            "Stainless Steel": ["SS", "S.S.", "STAINLESS"],
            "Brass": ["BRS", "BRASS"],
            "Aluminum": ["AL", "ALUM", "ALUMINUM"],
            "PVC": ["PVC", "POLYVINYL"],
            "2700K": ["27K", "2700K", "2700 K"],
            "3000K": ["30K", "3000K", "3000 K"],
            "5000K": ["50K", "5000K", "5000 K"]
        }

        observed_attr_map: Dict[str, Dict[str, dict]] = {}

        # 2. Incorporate allowed values from category_attributes.csv
        if os.path.exists(self.cat_attrs_csv_path):
            df_ca = pd.read_csv(self.cat_attrs_csv_path)
            for _, r in df_ca.iterrows():
                c_id = str(r['category_id']).strip()
                a_name = str(r['attribute_id']).strip()
                a_type = str(r['attribute_type']).strip()
                a_uom = str(r['unit_of_measure']).strip() if pd.notna(r['unit_of_measure']) else ""
                allowed_str = str(r['allowed_values']) if pd.notna(r['allowed_values']) else ""

                if allowed_str:
                    vals = [v.strip() for v in allowed_str.split(';') if v.strip()]
                    for val_str in vals:
                        if a_name not in observed_attr_map:
                            observed_attr_map[a_name] = {}

                        if val_str not in observed_attr_map[a_name]:
                            aliases_list = known_aliases.get(val_str, [])
                            observed_attr_map[a_name][val_str] = {
                                "attribute_type": a_type,
                                "canonical_value": val_str,
                                "normalized_value": val_str.lower(),
                                "aliases": ";".join(sorted(set(aliases_list))),
                                "unit": a_uom,
                                "categories": {c_id},
                                "count": 1
                            }
                        else:
                            observed_attr_map[a_name][val_str]["categories"].add(c_id)

        # Pre-seed standard material aliases for material & color_finish
        for mat_val, aliases_l in [("Stainless Steel", ["SS", "S.S."]), ("Brass", ["BRS", "BRASS"]), ("Aluminum", ["AL", "ALUM"])]:
            for target_a in ["material", "color_finish"]:
                if target_a in observed_attr_map:
                    if mat_val not in observed_attr_map[target_a]:
                        observed_attr_map[target_a][mat_val] = {
                            "attribute_type": "enum",
                            "canonical_value": mat_val,
                            "normalized_value": mat_val.lower(),
                            "aliases": ";".join(sorted(set(aliases_l))),
                            "unit": "",
                            "categories": set(),
                            "count": 1
                        }

        # 3. Extract observed attribute values from Phase 5 output
        df = pd.read_csv(self.enriched_csv_path)
        for _, row in df.iterrows():
            c_id = str(row.get("category_id") or "").strip()
            a_json = str(row.get("extracted_attributes_json") or "").strip()

            if not a_json or a_json == "{}":
                continue

            try:
                attrs = json.loads(a_json)
                for a_name, a_data in attrs.items():
                    val = a_data.get("value")
                    ev = str(a_data.get("evidence") or "").strip()

                    if val is None or pd.isna(val):
                        continue

                    val_str = str(val).strip()

                    if a_name not in observed_attr_map:
                        observed_attr_map[a_name] = {}

                    if val_str not in observed_attr_map[a_name]:
                        aliases_list = known_aliases.get(val_str, [ev] if ev and ev.lower() != val_str.lower() else [])

                        unit_str = ""
                        if a_name in ["diameter", "dimensions", "length", "width", "height"]:
                            unit_str = "in"
                        elif a_name == "voltage":
                            unit_str = "V"
                        elif a_name == "wattage":
                            unit_str = "W"
                        elif a_name == "color_temperature":
                            unit_str = "K"
                        elif a_name in ["pack_quantity", "piece_count"]:
                            unit_str = "pcs"
                        elif a_name == "grit":
                            unit_str = "Grit"

                        observed_attr_map[a_name][val_str] = {
                            "attribute_type": "measurement" if unit_str and a_name not in ["grit", "color_temperature"] else ("enum" if isinstance(val, str) else "integer"),
                            "canonical_value": val_str,
                            "normalized_value": val_str.lower(),
                            "aliases": ";".join(sorted(set(aliases_list))),
                            "unit": unit_str,
                            "categories": {c_id} if c_id else set(),
                            "count": 1
                        }
                    else:
                        observed_attr_map[a_name][val_str]["count"] += 1
                        if c_id:
                            observed_attr_map[a_name][val_str]["categories"].add(c_id)
            except Exception:
                pass

        # 4. Construct Attribute LOV Master (attribute_lov.csv)
        lov_rows = []
        lov_counter = 1

        for a_name, vals in observed_attr_map.items():
            for c_val, meta in vals.items():
                lov_id = f"LOV_{a_name.upper()}_{lov_counter:04d}"
                lov_counter += 1

                lov_rows.append({
                    "attribute_lov_id": lov_id,
                    "attribute_name": a_name,
                    "attribute_type": meta["attribute_type"],
                    "canonical_value": c_val,
                    "normalized_value": meta["normalized_value"],
                    "aliases": meta["aliases"],
                    "unit": meta["unit"],
                    "allowed_category_ids": ";".join(sorted(list(meta["categories"]))),
                    "source_count": meta["count"],
                    "is_active": True
                })

        lov_df = pd.DataFrame(lov_rows)
        os.makedirs(os.path.dirname(self.lov_output_path), exist_ok=True)
        lov_df.to_csv(self.lov_output_path, index=False)

        return lov_df, uom_df

    def validate_masters(self, lov_df: Optional[pd.DataFrame] = None, uom_df: Optional[pd.DataFrame] = None) -> bool:
        df_l = lov_df if lov_df is not None else pd.read_csv(self.lov_output_path)
        df_u = uom_df if uom_df is not None else pd.read_csv(self.uom_output_path)

        assert df_l['attribute_lov_id'].isna().sum() == 0, "LOV Validation Error: Empty attribute_lov_id!"
        assert df_l['canonical_value'].isna().sum() == 0, "LOV Validation Error: Empty canonical_value!"
        assert df_u['uom_id'].isna().sum() == 0, "UOM Validation Error: Empty uom_id!"
        assert df_u['canonical_uom'].isna().sum() == 0, "UOM Validation Error: Empty canonical_uom!"
        return True


if __name__ == "__main__":
    builder = LOVBuilder()
    df_lov, df_uom = builder.build_masters()
    builder.validate_masters(df_lov, df_uom)
    print(f"[SUCCESS] LOV Master built: {len(df_lov)} LOV entries in '{builder.lov_output_path}'")
    print(f"[SUCCESS] UOM Master built: {len(df_uom)} UOM entries in '{builder.uom_output_path}'")
