import sys
import json
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.understanding.schema import ProductInfo
from src.understanding.normalizer import ProductNormalizer

# Read current generated CSV
df = pd.read_csv('data/processed/understood_products.csv')

failed_df = df[df['understanding_status'] == 'failed'].head(20)
partial_df = df[df['understanding_status'] == 'partial'].head(20)

print("=" * 80)
print("PART 1: 20 SAMPLE FAILED PRODUCTS ANALYSIS")
print("=" * 80)

failed_reasons = {}

for idx, (_, row) in enumerate(failed_df.iterrows(), 1):
    desc = str(row['part_desc'])
    fallback_info = ProductNormalizer.deterministic_fallback_extract(desc)
    
    # Determine reason
    if not desc or desc.strip() == "":
        reason = "empty_description"
    elif fallback_info is None:
        reason = "missing_core_attribute (no MPN, Brand, or Product Type matched in fallback)"
    else:
        reason = "zero_extracted_attributes"
        
    failed_reasons[reason] = failed_reasons.get(reason, 0) + 1
    
    print(f"\n[{idx:02d}] FAILED PRODUCT: {desc}")
    print(f"     RAW FALLBACK RESULT: {fallback_info}")
    print(f"     PARSED JSON: {json.dumps(row.to_dict(), default=str, indent=2)}")
    print(f"     FAILURE REASON: {reason}")
    print("-" * 80)

print("\nSUMMARY OF FAILED REASONS (20 Sample Rows):")
for r, c in failed_reasons.items():
    print(f"  - {r}: {c}")


print("\n" + "=" * 80)
print("PART 2: 20 SAMPLE PARTIAL PRODUCTS ANALYSIS")
print("=" * 80)

partial_reasons = {}

for idx, (_, row) in enumerate(partial_df.iterrows(), 1):
    desc = str(row['part_desc'])
    
    # Check present vs missing fields
    present = []
    missing = []
    for col in ['manufacturer_part_number', 'brand', 'product_type', 'size', 'quantity']:
        val = row.get(col)
        if pd.notna(val) and str(val).strip() != "":
            present.append(col)
        else:
            missing.append(col)
            
    reason = f"Extracted {len(present)} field(s) ({', '.join(present)}); Missing: ({', '.join(missing)})"
    
    print(f"\n[{idx:02d}] PARTIAL PRODUCT: {desc}")
    print(f"     PRESENT FIELDS: {present}")
    print(f"     MISSING FIELDS: {missing}")
    print(f"     REASON: {reason}")
    print("-" * 80)
