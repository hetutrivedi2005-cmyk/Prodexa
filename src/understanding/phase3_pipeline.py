import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.understanding.master_data import MasterDataLoader
from src.understanding.resolver import EntityResolver, normalize_name


def run_phase3_pipeline(
    phase2_input_path: str = "data/processed/understood_products.csv",
    output_path: str = "data/processed/resolved_products.csv",
    input_raw_path: str = "data/raw/input.csv"
):
    print("=" * 80)
    print("PHASE 3 — MANUFACTURER & BRAND RESOLUTION PIPELINE")
    print("=" * 80)

    # 1. Load Master Reference Data & Entity Resolver
    print(f"\n[INFO] Loading master reference data from '{input_raw_path}' and Phase 2...")
    master_loader = MasterDataLoader(input_csv_path=input_raw_path, phase2_csv_path=phase2_input_path)
    resolver = EntityResolver(master_loader=master_loader)

    print(f"[INFO] Loaded {len(master_loader.manufacturer_records)} Manufacturer Reference Records.")
    print(f"[INFO] Loaded {len(master_loader.brand_records)} Brand Reference Records.")

    # 2. Load Phase 2 output CSV
    print(f"\n[INFO] Loading Phase 2 output from '{phase2_input_path}'...")
    p2_df = pd.read_csv(phase2_input_path)
    print(f"[INFO] Total input rows: {len(p2_df)}")

    # Prepare lists for new Phase 3 columns
    manuf_canonicals = []
    manuf_ids = []
    manuf_statuses = []
    manuf_methods = []
    manuf_confidences = []

    brand_canonicals = []
    brand_ids = []
    brand_statuses = []
    brand_methods = []
    brand_confidences = []

    # Track match statistics
    stats = {
        "manuf_exact": 0, "manuf_normalized": 0, "manuf_fuzzy": 0, "manuf_llm": 0, "manuf_ambiguous": 0, "manuf_unmatched": 0,
        "brand_exact": 0, "brand_normalized": 0, "brand_fuzzy": 0, "brand_llm": 0, "brand_ambiguous": 0, "brand_unmatched": 0,
    }

    unmatched_manufs_list = []
    ambiguous_manufs_list = []

    # 3. Process every product row
    for idx, row in p2_df.iterrows():
        raw_manuf = row.get("part_manuf")
        raw_brand = row.get("dib_brand") or row.get("e1_brand")
        p2_brand = row.get("brand")
        prod_desc = row.get("part_desc")

        # Resolve Manufacturer
        m_res = resolver.resolve_manufacturer(raw_manuf, product_desc=prod_desc)
        m_canon = m_res["manufacturer_canonical"]
        m_id = m_res["manufacturer_id"]
        m_status = m_res["manufacturer_match_status"]
        m_method = m_res["manufacturer_match_method"]
        m_conf = m_res["manufacturer_confidence"]

        manuf_canonicals.append(m_canon)
        manuf_ids.append(m_id)
        manuf_statuses.append(m_status)
        manuf_methods.append(m_method)
        manuf_confidences.append(m_conf)

        if m_status == "matched":
            stats[f"manuf_{m_method}"] = stats.get(f"manuf_{m_method}", 0) + 1
        elif m_status == "ambiguous":
            stats["manuf_ambiguous"] += 1
            ambiguous_manufs_list.append(str(raw_manuf))
        else:
            stats["manuf_unmatched"] += 1
            if raw_manuf and str(raw_manuf).strip() not in ["", "-", "nan"]:
                unmatched_manufs_list.append(str(raw_manuf))

        # Resolve Brand
        b_res = resolver.resolve_brand(raw_brand=raw_brand, phase2_brand=p2_brand, resolved_manufacturer=m_canon)
        b_canon = b_res["brand_canonical"]
        b_id = b_res["brand_id"]
        b_status = b_res["brand_match_status"]
        b_method = b_res["brand_match_method"]
        b_conf = b_res["brand_confidence"]

        brand_canonicals.append(b_canon)
        brand_ids.append(b_id)
        brand_statuses.append(b_status)
        brand_methods.append(b_method)
        brand_confidences.append(b_conf)

        if b_status == "matched":
            stats[f"brand_{b_method}"] = stats.get(f"brand_{b_method}", 0) + 1
        elif b_status == "ambiguous":
            stats["brand_ambiguous"] += 1
        else:
            stats["brand_unmatched"] += 1

    # 4. Construct enriched dataframe
    out_df = p2_df.copy()
    out_df["manufacturer_canonical"] = manuf_canonicals
    out_df["manufacturer_id"] = manuf_ids
    out_df["manufacturer_match_status"] = manuf_statuses
    out_df["manufacturer_match_method"] = manuf_methods
    out_df["manufacturer_confidence"] = manuf_confidences

    out_df["brand_canonical"] = brand_canonicals
    out_df["brand_id"] = brand_ids
    out_df["brand_match_status"] = brand_statuses
    out_df["brand_match_method"] = brand_methods
    out_df["brand_confidence"] = brand_confidences

    # 5. Master Data Integrity Validation
    print("\n" + "=" * 80)
    print("VALIDATING ENRICHED OUTPUT AGAINST REFERENCE DATA")
    print("=" * 80)

    # Check non-null manufacturer canonicals
    invalid_m_canon = [m for m in out_df["manufacturer_canonical"].dropna() if m not in master_loader.manufacturer_records]
    print(f"Invalid / Invented Manufacturer Canonicals: {len(invalid_m_canon)} -> {invalid_m_canon}")

    # Check non-null brand canonicals
    invalid_b_canon = [b for b in out_df["brand_canonical"].dropna() if b not in master_loader.brand_records]
    print(f"Invalid / Invented Brand Canonicals: {len(invalid_b_canon)} -> {invalid_b_canon}")

    assert len(invalid_m_canon) == 0, "ERROR: Found invented manufacturer canonical names!"
    assert len(invalid_b_canon) == 0, "ERROR: Found invented brand canonical names!"

    # 6. Save resolved_products.csv
    out_df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Successfully saved resolved output to '{output_path}' ({len(out_df)} rows).")

    # 7. Print Comprehensive Summary Report
    print("\n" + "=" * 80)
    print("PHASE 3 — STATISTICAL MATCHING REPORT")
    print("=" * 80)

    tot = len(out_df)
    m_matched = stats["manuf_exact"] + stats["manuf_normalized"] + stats["manuf_fuzzy"] + stats["manuf_llm"]
    b_matched = stats["brand_exact"] + stats["brand_normalized"] + stats["brand_fuzzy"] + stats["brand_llm"]

    m_rate = (m_matched / tot) * 100
    b_rate = (b_matched / tot) * 100

    print(f"\nTotal Products Processed: {tot}")

    print("\nMANUFACTURER RESOLUTION STATS:")
    print(f"  Exact Matches      : {stats['manuf_exact']:<5} ({(stats['manuf_exact']/tot)*100:.1f}%)")
    print(f"  Normalized Matches : {stats['manuf_normalized']:<5} ({(stats['manuf_normalized']/tot)*100:.1f}%)")
    print(f"  Fuzzy Matches      : {stats['manuf_fuzzy']:<5} ({(stats['manuf_fuzzy']/tot)*100:.1f}%)")
    print(f"  LLM Matches        : {stats['manuf_llm']:<5} ({(stats['manuf_llm']/tot)*100:.1f}%)")
    print(f"  Ambiguous          : {stats['manuf_ambiguous']:<5} ({(stats['manuf_ambiguous']/tot)*100:.1f}%)")
    print(f"  Unmatched          : {stats['manuf_unmatched']:<5} ({(stats['manuf_unmatched']/tot)*100:.1f}%)")
    print(f"  --> Manufacturer Match Rate: {m_rate:.1f}%")

    print("\nBRAND RESOLUTION STATS:")
    print(f"  Exact Matches      : {stats['brand_exact']:<5} ({(stats['brand_exact']/tot)*100:.1f}%)")
    print(f"  Normalized Matches : {stats['brand_normalized']:<5} ({(stats['brand_normalized']/tot)*100:.1f}%)")
    print(f"  Fuzzy Matches      : {stats['brand_fuzzy']:<5} ({(stats['brand_fuzzy']/tot)*100:.1f}%)")
    print(f"  LLM Matches        : {stats['brand_llm']:<5} ({(stats['brand_llm']/tot)*100:.1f}%)")
    print(f"  Ambiguous          : {stats['brand_ambiguous']:<5} ({(stats['brand_ambiguous']/tot)*100:.1f}%)")
    print(f"  Unmatched          : {stats['brand_unmatched']:<5} ({(stats['brand_unmatched']/tot)*100:.1f}%)")
    print(f"  --> Brand Match Rate       : {b_rate:.1f}%")

    print("\n" + "=" * 80)
    print("TOP 10 UNMATCHED MANUFACTURERS")
    print("=" * 80)
    unmatched_counts = pd.Series(unmatched_manufs_list).value_counts().head(10)
    print(unmatched_counts.to_string() if not unmatched_counts.empty else "None (0 unmatched)")

    print("\n" + "=" * 80)
    print("TOP 10 AMBIGUOUS MANUFACTURERS")
    print("=" * 80)
    ambig_counts = pd.Series(ambiguous_manufs_list).value_counts().head(10)
    print(ambig_counts.to_string() if not ambig_counts.empty else "None (0 ambiguous)")

    print("\n" + "=" * 80)
    print("REAL RESOLUTION EXAMPLES (First 10 Rows)")
    print("=" * 80)
    sample_cols = [
        "part_manuf", "manufacturer_canonical", "manufacturer_match_method", "manufacturer_confidence",
        "brand", "brand_canonical", "brand_match_method", "brand_confidence"
    ]
    print(out_df[sample_cols].head(10).to_string())


if __name__ == "__main__":
    run_phase3_pipeline()
