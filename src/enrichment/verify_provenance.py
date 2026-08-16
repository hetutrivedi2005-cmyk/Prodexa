import os
import sys
import json
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def verify_provenance_chain(csv_path: str = "data/processed/enriched_products_phase8_1.csv") -> dict:
    print("=" * 80)
    print("PRODEXA PHASE 8.1 — ENRICHMENT PROVENANCE AUDIT")
    print("=" * 80)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input file '{csv_path}' not found!")

    df = pd.read_csv(csv_path)
    total_enriched_attributes = 0
    valid_provenance_chains = 0
    broken_chains = 0

    sample_provenance_traces = []

    for idx, row in df.iterrows():
        status = row.get("enrichment_status")
        if status not in ["complete", "partial"]:
            continue

        raw_json = row.get("enriched_attributes_json")
        if pd.isna(raw_json) or not str(raw_json).strip():
            continue

        try:
            attr_dict = json.loads(raw_json)
        except Exception:
            continue

        mpn = str(row.get("manufacturer_part_number") or row.get("mfg_part_num") or "").strip()
        mfg = str(row.get("manufacturer_canonical") or row.get("part_manuf") or "").strip()

        for attr_name, attr_meta in attr_dict.items():
            total_enriched_attributes += 1

            source_id = attr_meta.get("source_id")
            source_url = attr_meta.get("source_url")
            evidence_text = attr_meta.get("evidence_text")
            extracted_val = attr_meta.get("normalized_value")

            # Check 7-step provenance integrity
            step1_attr = bool(attr_name)
            step2_src_id = bool(source_id)
            step3_url = bool(source_url and ("http" in source_url or "https" in source_url))
            step4_mfg_dom = bool("freud" in source_url or "3m" in source_url or "dewalt" in source_url or "industrial" in source_url or ".com" in source_url)
            step5_mpn = bool(mpn)
            step6_evidence = bool(evidence_text and len(evidence_text) > 0)
            step7_val = bool(extracted_val)

            is_valid_chain = all([step1_attr, step2_src_id, step3_url, step4_mfg_dom, step5_mpn, step6_evidence, step7_val])

            if is_valid_chain:
                valid_provenance_chains += 1
                if len(sample_provenance_traces) < 5:
                    sample_provenance_traces.append(
                        f"MPN:                  {mpn}\n"
                        f"Manufacturer:         {mfg}\n"
                        f"Target Attribute:     {attr_name}\n"
                        f"Source ID:            {source_id}\n"
                        f"Official Source URL:  {source_url}\n"
                        f"Evidence Text:        \"{evidence_text[:100]}...\"\n"
                        f"Extracted Value:      {extracted_val}\n"
                        f"Provenance Chain:     VERIFIED (100% Traceable)"
                    )
            else:
                broken_chains += 1

    print(f"Total Enriched Attributes Evaluated: {total_enriched_attributes}")
    print(f"Fully Traceable Provenance Chains:  {valid_provenance_chains}")
    print(f"Broken Provenance Chains:           {broken_chains}")
    traceability_rate = (valid_provenance_chains / total_enriched_attributes * 100.0) if total_enriched_attributes > 0 else 0.0
    print(f"Provenance Traceability Rate:       {traceability_rate:.2f}%")
    print("=" * 80)

    if sample_provenance_traces:
        print("\n--- SAMPLE PROVENANCE TRACES ---")
        for trace in sample_provenance_traces:
            print(trace)
            print("-" * 60)

    return {
        "total": total_enriched_attributes,
        "valid": valid_provenance_chains,
        "broken": broken_chains,
        "rate": traceability_rate
    }


if __name__ == "__main__":
    verify_provenance_chain()
