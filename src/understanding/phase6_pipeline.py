import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Set

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.understanding.lov_builder import LOVBuilder
from src.understanding.lov_engine import LOVResolver


def run_phase6_pipeline(
    enriched_input_path: str = "data/processed/attributes_enriched_products.csv",
    lov_output_path: str = "data/master/attribute_lov.csv",
    uom_output_path: str = "data/master/uom_master.csv",
    output_path: str = "data/processed/lov_resolved_products.csv",
    report_output_path: str = "reports/phase6_lov_report.txt"
):
    print("=" * 80)
    print("PRODEXA PHASE 6 — CONTROLLED LOV VALUE RESOLUTION PIPELINE")
    print("=" * 80)

    # 1. Build masters if needed
    print(f"\n[INFO] Step 1: Building LOV and UOM master files...")
    builder = LOVBuilder(enriched_csv_path=enriched_input_path, lov_output_path=lov_output_path, uom_output_path=uom_output_path)
    df_lov, df_uom = builder.build_masters()
    builder.validate_masters(df_lov, df_uom)
    print(f"[SUCCESS] LOV master entries: {len(df_lov)}, UOM master entries: {len(df_uom)}")

    # 2. Initialize LOV Resolver Engine
    print(f"\n[INFO] Step 2: Initializing LOVResolver Engine...")
    resolver = LOVResolver(lov_csv_path=lov_output_path, uom_csv_path=uom_output_path)

    # 3. Read Phase 5 input
    print(f"[INFO] Reading Phase 5 input from '{enriched_input_path}'...")
    df_in = pd.read_csv(enriched_input_path)
    total_input_rows = len(df_in)
    print(f"[INFO] Total input rows: {total_input_rows}")

    # Output column arrays
    lov_jsons = []
    statuses = []
    methods = []
    confidences = []
    values_resolved_list = []
    values_unresolved_list = []

    # Resolution counters
    status_counts = {"resolved": 0, "partial": 0, "ambiguous": 0, "unresolved": 0}
    method_counts = {
        "exact": 0,
        "normalized": 0,
        "alias": 0,
        "unit_normalization": 0,
        "numeric_normalization": 0,
        "fuzzy": 0,
        "llm": 0,
        "unresolved": 0
    }

    total_attrs_received = 0
    total_attrs_resolved = 0
    total_attrs_unresolved = 0
    total_attrs_ambiguous = 0

    comparison_logs = []  # List of before/after log entries

    # 4. Resolve LOV values for all products
    for idx, row in df_in.iterrows():
        c_id = row.get("category_id")
        a_json = str(row.get("extracted_attributes_json") or "").strip()

        source_fields = [
            row.get("part_desc"), row.get("size"), row.get("quantity"),
            row.get("product_type"), row.get("brand_canonical") or row.get("brand"),
            row.get("manufacturer_canonical") or row.get("part_manuf"),
            row.get("mfg_part_num"), row.get("manufacturer_part_number")
        ]

        product_lov_dict = {}
        row_resolved_cnt = 0
        row_unresolved_cnt = 0
        row_used_methods = set()

        if a_json and a_json != "{}":
            try:
                attrs = json.loads(a_json)
                total_attrs_received += len(attrs)

                for a_name, a_item in attrs.items():
                    raw_val = a_item.get("value")
                    res = resolver.resolve_value(c_id, a_name, raw_val, source_fields)

                    product_lov_dict[a_name] = res

                    mth = res["method"]
                    st = res["status"]
                    row_used_methods.add(mth)
                    method_counts[mth] = method_counts.get(mth, 0) + 1

                    if st == "resolved":
                        row_resolved_cnt += 1
                        total_attrs_resolved += 1
                    elif st == "ambiguous":
                        row_unresolved_cnt += 1
                        total_attrs_ambiguous += 1
                    else:
                        row_unresolved_cnt += 1
                        total_attrs_unresolved += 1

                    # Log comparison entry
                    comparison_logs.append({
                        "raw_value": str(raw_val),
                        "normalized_value": str(raw_val).lower().strip(),
                        "canonical_value": str(res["canonical_value"]),
                        "method": mth,
                        "confidence": res["confidence"],
                        "status": st
                    })
            except Exception:
                pass

        # Determine row-level status
        if total_attrs_received == 0 or (row_resolved_cnt == 0 and row_unresolved_cnt == 0):
            row_st = "unresolved"
            row_mth = "unresolved"
            row_conf = 0.0
        elif row_unresolved_cnt == 0:
            row_st = "resolved"
            row_mth = "alias" if "alias" in row_used_methods else ("exact" if "exact" in row_used_methods else list(row_used_methods)[0])
            row_conf = float(np.mean([item["confidence"] for item in product_lov_dict.values()]))
        elif row_resolved_cnt > 0:
            row_st = "partial"
            row_mth = "partial"
            row_conf = float(np.mean([item["confidence"] for item in product_lov_dict.values()]))
        else:
            row_st = "unresolved"
            row_mth = "unresolved"
            row_conf = 0.0

        lov_jsons.append(json.dumps(product_lov_dict))
        statuses.append(row_st)
        methods.append(row_mth)
        confidences.append(round(row_conf, 4))
        values_resolved_list.append(row_resolved_cnt)
        values_unresolved_list.append(row_unresolved_cnt)

        status_counts[row_st] = status_counts.get(row_st, 0) + 1

    # 5. Construct output DataFrame
    out_df = df_in.copy()
    out_df["lov_resolved_attributes_json"] = lov_jsons
    out_df["lov_resolution_status"] = statuses
    out_df["lov_resolution_method"] = methods
    out_df["lov_resolution_confidence"] = confidences
    out_df["lov_values_resolved"] = values_resolved_list
    out_df["lov_values_unresolved"] = values_unresolved_list

    out_df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] LOV resolved products saved to '{output_path}' ({len(out_df)} rows, {len(out_df.columns)} columns).")

    # 6. Generate Quality & Comparison Report
    attr_confidences = []
    for p_json in lov_jsons:
        if p_json and p_json != "{}":
            parsed_dict = json.loads(p_json)
            for item in parsed_dict.values():
                if item.get("confidence") is not None:
                    attr_confidences.append(float(item["confidence"]))

    attr_avg_conf = float(np.mean(attr_confidences)) if attr_confidences else 0.0
    prod_coverage_conf = float(np.mean(confidences))
    res_rate = (total_attrs_resolved / total_attrs_received * 100.0) if total_attrs_received > 0 else 0.0

    report_lines = [
        "============================================================",
        "PRODEXA PHASE 6 — LOV RESOLUTION REPORT",
        "============================================================",
        f"Total products:                  {total_input_rows}",
        f"Total attributes received:       {total_attrs_received}",
        f"Resolved attributes:             {total_attrs_resolved}",
        f"Unresolved attributes:           {total_attrs_unresolved}",
        f"Ambiguous attributes:            {total_attrs_ambiguous}",
        f"Resolution rate:                 {res_rate:.2f}%",
        "",
        f"Exact matches:                   {method_counts['exact']}",
        f"Normalized matches:              {method_counts['normalized']}",
        f"Alias matches:                   {method_counts['alias']}",
        f"Unit normalization:              {method_counts['unit_normalization']}",
        f"Numeric normalization:           {method_counts['numeric_normalization']}",
        f"Fuzzy matches:                   {method_counts['fuzzy']}",
        f"LLM resolutions:                 {method_counts['llm']}",
        f"Unresolved:                      {method_counts['unresolved']}",
        "",
        f"LLM calls:                       {resolver.llm_stats['calls']}",
        f"LLM accepted:                    {resolver.llm_stats['accepted']}",
        f"LLM rejected:                    {resolver.llm_stats['rejected']}",
        "",
        f"Attribute Resolution Confidence: {attr_avg_conf:.4f}",
        f"Overall Dataset Coverage Conf:   {prod_coverage_conf:.4f}",
        "============================================================",
        "",
        "============================================================",
        "MANDATORY BEFORE / AFTER COMPARISON EXAMPLES",
        "RAW VALUE -> NORMALIZED VALUE -> CANONICAL LOV VALUE -> METHOD -> CONFIDENCE -> STATUS",
        "============================================================"
    ]

    for entry in comparison_logs[:30]:
        report_lines.append(
            f"RAW: '{entry['raw_value']}' -> NORM: '{entry['normalized_value']}' -> CANONICAL: '{entry['canonical_value']}' | METHOD: {entry['method']} | CONF: {entry['confidence']} | STATUS: {entry['status']}"
        )

    os.makedirs(os.path.dirname(report_output_path), exist_ok=True)
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[SUCCESS] Quality report saved to '{report_output_path}'.")
    print("\n".join(report_lines[:26]))


if __name__ == "__main__":
    run_phase6_pipeline()
