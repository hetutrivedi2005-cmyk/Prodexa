import os
import sys
import json
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.understanding.attribute_schema_builder import AttributeSchemaBuilder
from src.understanding.attribute_extractor import CategoryAttributeExtractor, ground_text_in_fields


def run_phase5_pipeline(
    classified_input_path: str = "data/processed/classified_products.csv",
    schema_output_path: str = "data/master/category_attributes.csv",
    output_path: str = "data/processed/attributes_enriched_products.csv"
):
    print("=" * 80)
    print("PRODEXA PHASE 5 — CATEGORY-SPECIFIC ATTRIBUTE EXTRACTION PIPELINE")
    print("=" * 80)

    # 1. Build and validate category attribute schema
    print(f"\n[INFO] Step 1: Building attribute schema from '{classified_input_path}'...")
    schema_builder = AttributeSchemaBuilder(classified_csv_path=classified_input_path, output_csv_path=schema_output_path)
    schema_df = schema_builder.build_schema()
    schema_builder.validate_schema(schema_df)
    print(f"[SUCCESS] Attribute master schema built & validated: {len(schema_df)} attribute records saved to '{schema_output_path}'.")

    # 2. Initialize Extractor
    print(f"\n[INFO] Step 2: Initializing CategoryAttributeExtractor...")
    extractor = CategoryAttributeExtractor(schema_csv_path=schema_output_path)

    # 3. Read classified products input
    print(f"[INFO] Reading classified products from '{classified_input_path}'...")
    class_df = pd.read_csv(classified_input_path)
    total_input_rows = len(class_df)
    print(f"[INFO] Total input rows: {total_input_rows}")

    # Output column lists
    attr_jsons = []
    statuses = []
    methods = []
    confidences = []
    val_statuses = []

    # Stat counters
    status_counts = {"complete": 0, "partial": 0, "none": 0, "failed": 0}
    method_counts = {"rule": 0, "llm": 0, "hybrid": 0, "none": 0}
    validation_counts = {"valid": 0, "partial": 0, "invalid": 0}

    total_attrs_extracted = 0
    extracted_attr_frequencies: Dict[str, int] = {}
    category_attr_counts: Dict[str, int] = {}

    unknown_rejected = 0
    ungrounded_rejected = 0
    invalid_rejected = 0

    # 4. Extract attributes for all products
    for idx, row in class_df.iterrows():
        cat_id = row.get("category_id")
        p_desc = row.get("part_desc")
        p_size = row.get("size")
        p_qty = row.get("quantity")
        p_type = row.get("product_type")
        p_brand = row.get("brand_canonical") or row.get("brand")
        p_manuf = row.get("manufacturer_canonical") or row.get("part_manuf")
        p_mfg_num = row.get("mfg_part_num") or row.get("manufacturer_part_number")

        res = extractor.extract_product_attributes(
            category_id=cat_id,
            part_desc=p_desc,
            size=p_size,
            quantity=p_qty,
            product_type=p_type,
            brand=p_brand,
            manufacturer=p_manuf,
            mfg_part_num=p_mfg_num
        )

        a_json = res["extracted_attributes_json"]
        st = res["attribute_extraction_status"]
        mth = res["attribute_extraction_method"]
        conf = res["attribute_confidence"]
        v_st = res["attribute_validation_status"]

        attr_jsons.append(a_json)
        statuses.append(st)
        methods.append(mth)
        confidences.append(conf)
        val_statuses.append(v_st)

        status_counts[st] = status_counts.get(st, 0) + 1
        method_counts[mth] = method_counts.get(mth, 0) + 1
        validation_counts[v_st] = validation_counts.get(v_st, 0) + 1

        try:
            parsed_a = json.loads(a_json)
            total_attrs_extracted += len(parsed_a)
            for a_key in parsed_a.keys():
                extracted_attr_frequencies[a_key] = extracted_attr_frequencies.get(a_key, 0) + 1

            if cat_id and pd.notna(cat_id):
                category_attr_counts[str(cat_id)] = category_attr_counts.get(str(cat_id), 0) + len(parsed_a)
        except Exception:
            pass

    # 5. Construct enriched dataframe
    out_df = class_df.copy()
    out_df["extracted_attributes_json"] = attr_jsons
    out_df["attribute_extraction_status"] = statuses
    out_df["attribute_extraction_method"] = methods
    out_df["attribute_confidence"] = confidences
    out_df["attribute_validation_status"] = val_statuses

    # Save output CSV
    out_df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Attributes enriched products saved to '{output_path}' ({len(out_df)} rows, {len(out_df.columns)} columns).")

    # =========================================================================
    # SECTION 20 — MANDATORY FINAL INTEGRITY AUDIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 20 — MANDATORY FINAL INTEGRITY AUDIT")
    print("=" * 80)

    assert os.path.exists(classified_input_path), "Integrity Error: classified_products.csv does not exist!"
    assert os.path.exists(schema_output_path), "Integrity Error: category_attributes.csv does not exist!"
    assert os.path.exists(output_path), "Integrity Error: attributes_enriched_products.csv does not exist!"
    assert len(out_df) == total_input_rows, f"Integrity Error: Row count mismatch! Expected {total_input_rows}, got {len(out_df)}"

    # Audit attribute json validity & category permission
    for _, r in out_df.iterrows():
        c_id = r.get("category_id")
        a_str = r.get("extracted_attributes_json")

        assert pd.notna(a_str), "Integrity Error: Null extracted_attributes_json!"
        parsed = json.loads(a_str)
        assert not r.get("extracted_attributes_json").startswith("```"), "Integrity Error: Found markdown in JSON!"

        if c_id and pd.notna(c_id) and str(c_id).strip() in extractor.category_schemas:
            allowed_keys = set(extractor.category_schemas[str(c_id).strip()].keys())
            for k, item in parsed.items():
                assert k in allowed_keys, f"Integrity Error: Extracted attribute '{k}' not allowed for category '{c_id}'!"
                assert "value" in item and "evidence" in item and "confidence" in item, "Integrity Error: Missing item keys!"
                assert 0.0 <= item["confidence"] <= 1.0, "Integrity Error: Confidence out of bounds!"

    print("[SUCCESS] ALL SECTION 20 INTEGRITY AUDIT CHECKS PASSED CLEANLY!")

    # =========================================================================
    # SECTION 21 — FINAL REPORT
    # =========================================================================
    avg_conf = float(np.mean(confidences))

    print("\n" + "=" * 80)
    print("============================================================")
    print("PRODEXA PHASE 5 — ATTRIBUTE EXTRACTION REPORT")
    print("============================================================")
    print(f"Total products:                           {total_input_rows}")
    print(f"Products with complete extraction:       {status_counts['complete']}")
    print(f"Products with partial extraction:        {status_counts['partial']}")
    print(f"Products with no extractable attributes: {status_counts['none']}")
    print(f"Failed:                                   {status_counts['failed']}")

    print(f"\nTotal attributes extracted:               {total_attrs_extracted}")
    print(f"Rule extractions:                         {method_counts['rule']}")
    print(f"LLM extractions:                          {method_counts['llm']}")
    print(f"Hybrid extractions:                       {method_counts['hybrid']}")

    print(f"\nLLM calls:                                {extractor.llm_stats['calls']}")
    print(f"LLM failures:                             {extractor.llm_stats['rejected']}")
    print(f"Unknown attributes rejected:              {unknown_rejected}")
    print(f"Ungrounded values rejected:               {ungrounded_rejected}")
    print(f"Invalid values rejected:                  {invalid_rejected}")

    print(f"\nAverage confidence:                       {avg_conf:.4f}")
    print("============================================================")

    print("\n" + "=" * 80)
    print("TOP 20 EXTRACTED ATTRIBUTES BY FREQUENCY")
    print("=" * 80)
    top_attrs = pd.Series(extracted_attr_frequencies).sort_values(ascending=False).head(20)
    print(top_attrs.to_string() if not top_attrs.empty else "None")

    print("\n" + "=" * 80)
    print("TOP 10 CATEGORIES BY ATTRIBUTE COUNT")
    print("=" * 80)
    top_cat_counts = pd.Series(category_attr_counts).sort_values(ascending=False).head(10)
    print(top_cat_counts.to_string() if not top_cat_counts.empty else "None")

    print("\n" + "=" * 80)
    print("20 REAL ENRICHED EXAMPLES")
    print("=" * 80)
    sample_cols = ["part_desc", "category_name", "extracted_attributes_json", "attribute_extraction_method", "attribute_confidence"]
    sample_20 = out_df[sample_cols].head(20)
    for idx_s, row_s in sample_20.iterrows():
        print(f"[{idx_s+1:02d}] {row_s['part_desc']}")
        print(f"     -> Category: {row_s['category_name']}")
        print(f"     -> Attributes: {row_s['extracted_attributes_json']}")
        print(f"     -> Method: {row_s['attribute_extraction_method']} | Confidence: {row_s['attribute_confidence']}")
        print("-" * 80)


if __name__ == "__main__":
    run_phase5_pipeline()
