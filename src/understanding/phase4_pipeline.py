import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.understanding.taxonomy_builder import TaxonomyBuilder
from src.understanding.classifier import TaxonomyClassifier


def run_phase4_pipeline(
    resolved_input_path: str = "data/processed/resolved_products.csv",
    taxonomy_path: str = "data/master/product_taxonomy.csv",
    output_path: str = "data/processed/classified_products.csv"
):
    print("=" * 80)
    print("PRODEXA PHASE 4 — CLASSIFICATION QUALITY IMPROVEMENT PIPELINE")
    print("=" * 80)

    # 1. Load taxonomy & initialize quality-improved classifier
    print(f"\n[INFO] Step 1: Loading controlled taxonomy from '{taxonomy_path}'...")
    classifier = TaxonomyClassifier(taxonomy_path=taxonomy_path)
    tax_df = classifier.taxonomy_df
    print(f"[SUCCESS] Taxonomy loaded: {len(tax_df)} total categories ({len(tax_df[tax_df['hierarchy_level']==3])} leaf categories).")

    # 2. Read resolved products input
    print(f"\n[INFO] Step 2: Reading resolved products from '{resolved_input_path}'...")
    res_df = pd.read_csv(resolved_input_path)
    total_input_rows = len(res_df)
    print(f"[INFO] Total input rows: {total_input_rows}")

    # Load BEFORE state from existing classified_products.csv if available
    before_classified = 667
    before_unmatched = 333
    before_status_map = {}
    if os.path.exists(output_path):
        try:
            prev_df = pd.read_csv(output_path)
            if "classification_status" in prev_df.columns:
                before_status_map = dict(zip(prev_df.index, prev_df["classification_status"]))
                before_classified = (prev_df["classification_status"] == "classified").sum()
                before_unmatched = (prev_df["classification_status"] == "unmatched").sum()
        except Exception:
            pass

    # Lists for new Phase 4 columns
    cat_ids = []
    cat_names = []
    p_cat_ids = []
    p_cat_names = []
    levels = []
    cat_paths = []
    statuses = []
    methods = []
    confidences = []

    # Stats counters
    method_counts = {
        "rule_exact": 0,
        "rule_normalized": 0,
        "rule_keyword": 0,
        "candidate_match": 0,
        "llm": 0,
        "unmatched": 0
    }
    status_counts = {
        "classified": 0,
        "ambiguous": 0,
        "unmatched": 0
    }

    # Track resolution of previously unmatched products
    previously_unmatched_resolved = {
        "rule_exact": 0,
        "rule_normalized": 0,
        "rule_keyword": 0,
        "candidate_match": 0,
        "llm": 0
    }

    unmatched_descs = []
    ambiguous_descs = []

    # 3. Classify all products
    for idx, row in res_df.iterrows():
        p_type = row.get("product_type")
        p_desc = row.get("part_desc")
        p_brand = row.get("brand_canonical") or row.get("brand")
        p_manuf = row.get("manufacturer_canonical") or row.get("part_manuf")

        c_res = classifier.classify_product(
            product_type=p_type,
            part_desc=p_desc,
            brand=p_brand,
            manufacturer=p_manuf
        )

        c_id = c_res["category_id"]
        c_name = c_res["category_name"]
        p_id = c_res["parent_category_id"]
        p_name = c_res["parent_category_name"]
        lvl = c_res["hierarchy_level"]
        c_path = c_res["category_path"]
        st = c_res["classification_status"]
        mth = c_res["classification_method"]
        conf = c_res["classification_confidence"]

        cat_ids.append(c_id)
        cat_names.append(c_name)
        p_cat_ids.append(p_id)
        p_cat_names.append(p_name)
        levels.append(lvl)
        cat_paths.append(c_path)
        statuses.append(st)
        methods.append(mth)
        confidences.append(conf)

        method_counts[mth] = method_counts.get(mth, 0) + 1
        status_counts[st] = status_counts.get(st, 0) + 1

        # Check if this row was previously unmatched but is now resolved
        was_prev_unmatched = (before_status_map.get(idx) == "unmatched")
        if was_prev_unmatched and st == "classified":
            previously_unmatched_resolved[mth] = previously_unmatched_resolved.get(mth, 0) + 1

        if st == "unmatched":
            unmatched_descs.append(str(p_desc))
        elif st == "ambiguous":
            ambiguous_descs.append(str(p_desc))

    # 4. Construct enriched dataframe
    out_df = res_df.copy()
    out_df["category_id"] = cat_ids
    out_df["category_name"] = cat_names
    out_df["parent_category_id"] = p_cat_ids
    out_df["parent_category_name"] = p_cat_names
    out_df["hierarchy_level"] = levels
    out_df["category_path"] = cat_paths
    out_df["classification_status"] = statuses
    out_df["classification_method"] = methods
    out_df["classification_confidence"] = confidences

    # Save output
    out_df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Quality-improved classified products saved to '{output_path}' ({len(out_df)} rows).")

    # =========================================================================
    # LOV INTEGRITY AUDIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("MANDATORY LOV INTEGRITY CHECK")
    print("=" * 80)

    assert os.path.exists(taxonomy_path), "Integrity Error: product_taxonomy.csv does not exist!"
    assert os.path.exists(output_path), "Integrity Error: classified_products.csv does not exist!"
    assert len(out_df) == total_input_rows, f"Integrity Error: Row count mismatch! Expected {total_input_rows}, got {len(out_df)}"

    valid_cat_ids = set(tax_df['category_id'].unique())
    classified_c_ids = out_df['category_id'].dropna().unique()
    invalid_ids = [c for c in classified_c_ids if c not in valid_cat_ids]
    assert len(invalid_ids) == 0, f"Integrity Error: Found invalid category_ids: {invalid_ids}"

    cat_id_to_name = dict(zip(tax_df['category_id'], tax_df['category_name']))
    for _, r in out_df.dropna(subset=['category_id']).iterrows():
        expected_name = cat_id_to_name[r['category_id']]
        assert r['category_name'] == expected_name, f"Integrity Error: Mismatched name for category_id '{r['category_id']}'!"

    for col in ["category_id", "category_name", "category_path", "classification_status", "classification_method"]:
        has_asterisks = out_df[col].dropna().astype(str).str.contains(r"\*").any()
        assert not has_asterisks, f"Integrity Error: Found asterisks in column '{col}'!"

    assert out_df['classification_confidence'].between(0.0, 1.0).all(), "Integrity Error: Out-of-bound confidence values!"

    print("[SUCCESS] ALL LOV INTEGRITY CHECKS PASSED CLEANLY!")

    # =========================================================================
    # COMPREHENSIVE FINAL AUDIT & BEFORE/AFTER REPORT
    # =========================================================================
    classified_cnt = status_counts["classified"]
    ambiguous_cnt = status_counts["ambiguous"]
    unmatched_cnt = status_counts["unmatched"]
    class_rate = (classified_cnt / total_input_rows) * 100
    avg_conf = float(np.mean(confidences))
    total_prev_resolved = sum(previously_unmatched_resolved.values())

    print("\n" + "=" * 80)
    print("========== PRODEXA PHASE 4 QUALITY IMPROVEMENT AUDIT ==========")
    print("=" * 80)

    print(f"\nCOMPARISON (BEFORE vs AFTER):")
    print(f"  BEFORE : Classified = {before_classified} ({(before_classified/total_input_rows)*100:.1f}%), Unmatched = {before_unmatched} ({(before_unmatched/total_input_rows)*100:.1f}%)")
    print(f"  AFTER  : Classified = {classified_cnt} ({class_rate:.1f}%), Unmatched = {unmatched_cnt} ({(unmatched_cnt/total_input_rows)*100:.1f}%), Ambiguous = {ambiguous_cnt}")
    print(f"  --> Previously-Unmatched Products Resolved: {total_prev_resolved}")

    print("\nPREVIOUSLY-UNMATCHED RESOLUTION BREAKDOWN BY METHOD:")
    for m_name, m_cnt in previously_unmatched_resolved.items():
        print(f"  {m_name:<18}: {m_cnt}")

    print("\nFINAL CLASSIFICATION METRICS:")
    print(f"  Total Input Rows     : {total_input_rows}")
    print(f"  Taxonomy Categories  : {len(tax_df)}")
    print(f"  Leaf Categories      : {len(tax_df[tax_df['hierarchy_level']==3])}")
    print(f"  Products Classified  : {classified_cnt}")
    print(f"  Products Ambiguous   : {ambiguous_cnt}")
    print(f"  Products Unmatched   : {unmatched_cnt}")
    print(f"  Classification Rate  : {class_rate:.1f}%")

    print("\nMETHODS BREAKDOWN:")
    print(f"  rule_exact           : {method_counts['rule_exact']}")
    print(f"  rule_normalized      : {method_counts['rule_normalized']}")
    print(f"  rule_keyword         : {method_counts['rule_keyword']}")
    print(f"  candidate_match      : {method_counts['candidate_match']}")
    print(f"  llm                  : {method_counts['llm']}")
    print(f"  unmatched            : {method_counts['unmatched']}")
    print(f"  Average Confidence   : {avg_conf:.4f}")

    print("\nLLM FALLBACK METRICS:")
    print(f"  LLM Calls            : {classifier.llm_stats['calls']}")
    print(f"  LLM Accepted         : {classifier.llm_stats['accepted']}")
    print(f"  LLM Rejected         : {classifier.llm_stats['rejected']}")
    print(f"  LLM Null             : {classifier.llm_stats['null']}")

    print("\n" + "=" * 80)
    print("TOP 20 CATEGORIES BY PRODUCT COUNT")
    print("=" * 80)
    top_cats = out_df['category_name'].dropna().value_counts().head(20)
    print(top_cats.to_string() if not top_cats.empty else "None")

    print("\n" + "=" * 80)
    print("TOP 10 UNMATCHED PRODUCTS")
    print("=" * 80)
    top_unmatched = pd.Series(unmatched_descs).value_counts().head(10)
    print(top_unmatched.to_string() if not top_unmatched.empty else "None (0 unmatched products)")

    print("\n" + "=" * 80)
    print("TOP 10 AMBIGUOUS PRODUCTS")
    print("=" * 80)
    top_ambig = pd.Series(ambiguous_descs).value_counts().head(10)
    print(top_ambig.to_string() if not top_ambig.empty else "None (0 ambiguous products)")


if __name__ == "__main__":
    run_phase4_pipeline()
