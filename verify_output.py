import sys
import pandas as pd
from pathlib import Path

csv_path = Path("data/processed/understood_products.csv")
if not csv_path.exists():
    print(f"[ERROR] {csv_path} does not exist yet!")
    sys.exit(1)

df = pd.read_csv(csv_path, dtype=str)

print("\n" + "=" * 80)
print("1. FIRST 10 ROWS OF GENERATED CSV")
print("=" * 80)
print(df.head(10).to_string())

print("\n" + "=" * 80)
print("2. ASTERISK & BACKTICK SEARCH IN COLUMNS AND VALUES")
print("=" * 80)

# Column check
asterisk_cols = [col for col in df.columns if "*" in str(col)]
backtick_cols = [col for col in df.columns if "`" in str(col)]
print(f"Columns with '*': {len(asterisk_cols)} -> {asterisk_cols}")
print(f"Columns with '`': {len(backtick_cols)} -> {backtick_cols}")

# Values check
asterisk_value_count = df.fillna("").astype(str).apply(lambda col: col.str.contains(r"\*", regex=True)).sum().sum()
backtick_value_count = df.fillna("").astype(str).apply(lambda col: col.str.contains(r"`", regex=True)).sum().sum()
print(f"Total cell values containing '*': {asterisk_value_count}")
print(f"Total cell values containing '`': {backtick_value_count}")

assert len(asterisk_cols) == 0, "Column names contain '*'"
assert len(backtick_cols) == 0, "Column names contain '`'"
assert asterisk_value_count == 0, "Cell values contain '*'"
assert backtick_value_count == 0, "Cell values contain '`'"

print("\n" + "=" * 80)
print("3. VERIFY SPECIFIC REQUIREMENT ROWS")
print("=" * 80)

desc_col = "part_desc" if "part_desc" in df.columns else "product_description"

# HIOLIT 5B-332-080
row_080 = df[df["manufacturer_part_number"] == "5B-332-080"]
print("\nHIOLIT 5B-332-080:")
print(row_080[["manufacturer_part_number", "brand", "product_type", "size", "quantity", "understanding_status"]].to_dict(orient="records"))

# HIOLIT 5B-332-120
row_120 = df[df["manufacturer_part_number"] == "5B-332-120"]
print("\nHIOLIT 5B-332-120:")
print(row_120[["manufacturer_part_number", "brand", "product_type", "size", "quantity", "understanding_status"]].to_dict(orient="records"))

# Diablo
row_diablo = df[df["manufacturer_part_number"] == "DCB518ASTS06G"]
print("\nDiablo DCB518ASTS06G:")
print(row_diablo[["manufacturer_part_number", "brand", "product_type", "size", "quantity", "understanding_status"]].to_dict(orient="records"))

# 3M 775L
row_3m = df[df["manufacturer_part_number"] == "775L"]
print("\n3M 775L (first matching row):")
print(row_3m[["manufacturer_part_number", "brand", "product_type", "size", "quantity", "understanding_status"]].head(1).to_dict(orient="records"))

print("\n" + "=" * 80)
print("4. FINAL STATUS BREAKDOWN COUNTS")
print("=" * 80)
if "understanding_status" in df.columns:
    print(df["understanding_status"].value_counts().to_string())

print("\n[SUCCESS] ALL CHECKS PASSED CLEANLY!")
