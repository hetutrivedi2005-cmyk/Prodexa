import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.understanding.uom_normalizer import UOMNormalizer


def run_phase7_pipeline(
    input_path: str = "data/processed/lov_resolved_products.csv",
    output_path: str = "data/processed/uom_normalized_products.csv",
    report_path: str = "reports/phase7_uom_report.txt"
):
    print("=" * 80)
    print("PRODEXA PHASE 7 — DETERMINISTIC UOM NORMALIZATION PIPELINE")
    print("=" * 80)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' not found! Run Phase 6 pipeline first.")

    normalizer = UOMNormalizer()
    df_p6 = pd.read_csv(input_path)
    total_input_rows = len(df_p6)
    print(f"[INFO] Input dataset '{input_path}' loaded ({total_input_rows} rows).")

    uom_jsons = []
    statuses = []
    methods = []
    confidences = []
    values_normalized_counts = []
    values_unresolved_counts = []

    total_uom_received = 0
    total_uom_normalized = 0
    total_uom_already_canonical = 0
    total_uom_transformed = 0
    total_uom_unresolved = 0
    total_uom_unsupported_unit = 0

    method_counts = {
        "already_canonical": 0,
        "unit_alias": 0,
        "decimal_normalization": 0,
        "fraction_normalization": 0,
        "mixed_fraction_normalization": 0,
        "unit_conversion": 0,
        "compound_dimension": 0,
        "unsupported": 0,
        "unsupported_unit": 0,
        "not_applicable": 0
    }

    before_after_examples = []

    for idx, row in df_p6.iterrows():
        c_id = str(row.get("category_id") or "").strip()
        lov_attr_json = str(row.get("lov_resolved_attributes_json") or "").strip()

        if not lov_attr_json or lov_attr_json == "{}":
            uom_jsons.append("{}")
            statuses.append("not_applicable")
            methods.append("not_applicable")
            confidences.append(1.0)
            values_normalized_counts.append(0)
            values_unresolved_counts.append(0)
            continue

        try:
            lov_attrs = json.loads(lov_attr_json)
        except Exception:
            uom_jsons.append("{}")
            statuses.append("unresolved")
            methods.append("unsupported")
            confidences.append(0.0)
            values_normalized_counts.append(0)
            values_unresolved_counts.append(0)
            continue

        row_uom_dict = {}
        row_norm_cnt = 0
        row_unres_cnt = 0
        row_methods = []
        row_confs = []

        for a_name, a_item in lov_attrs.items():
            raw_val = a_item.get("canonical_value") or a_item.get("value")
            if raw_val is None or pd.isna(raw_val):
                continue

            total_uom_received += 1
            norm_res = normalizer.normalize(raw_val, attribute_name=a_name, category_id=c_id)
            row_uom_dict[a_name] = norm_res

            st = norm_res["status"]
            mth = norm_res["method"]
            conf = norm_res["confidence"]

            row_methods.append(mth)
            row_confs.append(conf)

            if mth in method_counts:
                method_counts[mth] += 1

            if st in ["normalized", "already_canonical"]:
                row_norm_cnt += 1
                total_uom_normalized += 1
                if mth == "already_canonical":
                    total_uom_already_canonical += 1
                else:
                    total_uom_transformed += 1
            else:
                row_unres_cnt += 1
                total_uom_unresolved += 1
                if mth == "unsupported_unit":
                    total_uom_unsupported_unit += 1

            if len(before_after_examples) < 25:
                before_after_examples.append(
                    f"RAW: '{raw_val}' -> NORMALIZED: '{norm_res['normalized_value']}' | METHOD: {mth} | STATUS: {st}"
                )

        uom_jsons.append(json.dumps(row_uom_dict))
        values_normalized_counts.append(row_norm_cnt)
        values_unresolved_counts.append(row_unres_cnt)

        if row_norm_cnt == 0 and row_unres_cnt == 0:
            statuses.append("not_applicable")
            methods.append("not_applicable")
            confidences.append(1.0)
        elif row_unres_cnt == 0:
            statuses.append("normalized")
            methods.append(row_methods[0] if len(set(row_methods)) == 1 else "normalized")
            confidences.append(float(np.mean(row_confs)))
        elif row_norm_cnt > 0:
            statuses.append("partial")
            methods.append("partial")
            confidences.append(float(np.mean(row_confs)))
        else:
            statuses.append("unresolved")
            methods.append("unresolved")
            confidences.append(0.0)

    # Dynamic Column Preservation: Retain all existing Phase 6 columns
    out_df = df_p6.copy()
    out_df["uom_normalized_attributes_json"] = uom_jsons
    out_df["uom_normalization_status"] = statuses
    out_df["uom_normalization_method"] = methods
    out_df["uom_normalization_confidence"] = confidences
    out_df["uom_values_normalized"] = values_normalized_counts
    out_df["uom_values_unresolved"] = values_unresolved_counts

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out_df.to_csv(output_path, index=False)
    print(f"[SUCCESS] UOM normalized products saved to '{output_path}' ({len(out_df)} rows, {len(out_df.columns)} columns).")

    # Generate Phase 7 Quality Report
    success_rate = (total_uom_normalized / total_uom_received * 100.0) if total_uom_received > 0 else 0.0
    transform_rate = (total_uom_transformed / total_uom_received * 100.0) if total_uom_received > 0 else 0.0
    uom_confidences = [c for c in confidences if c is not None]
    avg_conf = float(np.mean(uom_confidences)) if uom_confidences else 1.0

    report_lines = [
        "============================================================",
        "PRODEXA PHASE 7 — UOM NORMALIZATION REPORT",
        "============================================================",
        f"Total products:                      {total_input_rows}",
        f"Total attribute values received:     {total_uom_received}",
        f"Already canonical:                   {total_uom_already_canonical}",
        f"Actually transformed:                {total_uom_transformed}",
        f"Unresolved values:                   {total_uom_unresolved}",
        f"Unsupported units:                   {total_uom_unsupported_unit}",
        f"Successful processing rate:          {success_rate:.2f}%",
        f"Transformation rate:                 {transform_rate:.2f}%",
        "",
        f"Decimal normalizations:              {method_counts['decimal_normalization']}",
        f"Fraction normalizations:             {method_counts['fraction_normalization']}",
        f"Mixed fraction normalizations:       {method_counts['mixed_fraction_normalization']}",
        f"Unit alias normalizations:           {method_counts['unit_alias']}",
        f"Unit conversions:                    {method_counts['unit_conversion']}",
        f"Compound dimensions:                 {method_counts['compound_dimension']}",
        "",
        f"AI/LLM calls:                        0",
        f"Deterministic confidence avg:        {avg_conf:.4f}",
        "============================================================",
        "",
        "============================================================",
        "20 REAL BEFORE -> AFTER EXAMPLES",
        "============================================================"
    ]
    report_lines.extend(before_after_examples[:20])

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[SUCCESS] Quality report saved to '{report_path}'.")
    print("\n".join(report_lines[:23]))


if __name__ == "__main__":
    run_phase7_pipeline()
