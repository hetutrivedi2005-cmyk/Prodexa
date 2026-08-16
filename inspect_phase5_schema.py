import pandas as pd

df = pd.read_csv('data/processed/classified_products.csv')

print("=" * 80)
print("INSPECTING CLASSIFIED PRODUCTS FOR PHASE 5 ATTRIBUTE SCHEMA DERIVATION")
print("=" * 80)

top_cats = df['category_id'].value_counts().head(15)
print("\nTOP 15 CLASSIFIED CATEGORIES:")
print(top_cats.to_string())

print("\n" + "=" * 80)
print("SAMPLE DESCRIPTIONS PER CATEGORY:")
print("=" * 80)

for cid, count in top_cats.items():
    cat_name = df[df['category_id'] == cid]['category_name'].iloc[0]
    samples = df[df['category_id'] == cid]['part_desc'].head(4).tolist()
    print(f"\n[{cid}] {cat_name} ({count} products):")
    for s in samples:
        print(f"  - {s}")
