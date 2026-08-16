import re
import pandas as pd

df = pd.read_csv('data/raw/input.csv')

print("=" * 80)
print("INSPECTING DATASET FOR MANUFACTURER & BRAND MASTER DATA")
print("=" * 80)

print(f"\n1. INPUT.CSV COLUMNS: {df.columns.tolist()}")

pm_list = df['Part_Manuf'].dropna().unique()
print(f"\n2. MANUFACTURER MASTER DATA FROM Part_Manuf (Total: {len(pm_list)})")

manuf_master = []
for pm in pm_list:
    pm_clean = str(pm).strip()
    match = re.search(r"^(.*?)\s*\(([^)]+)\)$", pm_clean)
    if match:
        name = match.group(1).strip()
        code = match.group(2).strip()
    else:
        name = pm_clean
        code = ""
    manuf_master.append({"raw": pm_clean, "canonical_name": name, "id": code})

manuf_df = pd.DataFrame(manuf_master)
print(manuf_df.head(20).to_string())

print("\n" + "=" * 80)
print("3. BRAND MASTER DATA FROM E1_Brand, DIB_Brand, Unilog_Brand & Phase 2 Brand")
print("=" * 80)

e1_brands = [b for b in df['E1_Brand'].dropna().unique() if not str(b).lower().startswith('--')]
dib_brands = [b for b in df['DIB_Brand'].dropna().unique() if not str(b).lower().startswith('--')]

print(f"E1 Brands ({len(e1_brands)}): {e1_brands}")
print(f"DIB Brands ({len(dib_brands)}): {dib_brands}")
