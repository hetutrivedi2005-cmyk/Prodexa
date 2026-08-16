import re
from typing import Dict, List, Tuple, Optional, Set
import pandas as pd


class MasterDataLoader:
    """
    Loads and structures Manufacturer & Brand Reference Data from the project's data files.
    - Treats Part_Manuf data from input.csv as Manufacturer Reference Data.
    - Generates internal canonical brand IDs (BRD_*).
    - Preserves known Manufacturer-to-Brand relationships.
    """

    def __init__(self, input_csv_path: str = "data/raw/input.csv", phase2_csv_path: str = "data/processed/understood_products.csv"):
        self.input_csv_path = input_csv_path
        self.phase2_csv_path = phase2_csv_path

        # Manufacturer Reference Data structures
        self.manufacturer_records: Dict[str, dict] = {}  # canonical_name -> record dict
        self.normalized_manuf_lookup: Dict[str, str] = {}  # normalized_name -> canonical_name
        self.manuf_id_lookup: Dict[str, str] = {}  # code/id -> canonical_name

        # Brand Reference Data structures
        self.brand_records: Dict[str, dict] = {}  # canonical_name -> record dict
        self.normalized_brand_lookup: Dict[str, str] = {}  # normalized_name -> canonical_name
        self.brand_id_lookup: Dict[str, str] = {}  # brand_id -> canonical_name

        # Manufacturer-to-Brand Relationships
        self.manuf_to_brands: Dict[str, Set[str]] = {}  # canonical_manuf -> set of canonical_brands
        self.brand_to_manufs: Dict[str, Set[str]] = {}  # canonical_brand -> set of canonical_manufs

        self._load_and_build()

    @staticmethod
    def normalize_key(val: str) -> str:
        if not val or not isinstance(val, str):
            return ""
        v = val.strip().lower()
        v = re.sub(r"[^\w\s]", " ", v)
        v = re.sub(r"\s+", " ", v).strip()
        return v

    def _load_and_build(self):
        # 1. Load input.csv for manufacturer reference data & brand feeds
        input_df = pd.read_csv(self.input_csv_path)

        # Build Manufacturer Reference Data from Part_Manuf
        if "Part_Manuf" in input_df.columns:
            pm_unique = input_df["Part_Manuf"].dropna().unique()
            for raw_pm in pm_unique:
                pm_str = str(raw_pm).strip()
                if not pm_str or pm_str in ["-", "nan", "none"]:
                    continue

                match = re.search(r"^(.*?)\s*\(([^)]+)\)$", pm_str)
                if match:
                    canonical_name = match.group(1).strip()
                    ref_code = match.group(2).strip()
                else:
                    canonical_name = pm_str
                    ref_code = ""

                norm_key = self.normalize_key(canonical_name)

                if canonical_name not in self.manufacturer_records:
                    self.manufacturer_records[canonical_name] = {
                        "canonical_name": canonical_name,
                        "reference_id": ref_code,
                        "raw_examples": [pm_str]
                    }
                else:
                    if ref_code and not self.manufacturer_records[canonical_name]["reference_id"]:
                        self.manufacturer_records[canonical_name]["reference_id"] = ref_code
                    self.manufacturer_records[canonical_name]["raw_examples"].append(pm_str)

                if norm_key:
                    self.normalized_manuf_lookup[norm_key] = canonical_name

                # Add alias without suffixes like Inc, LLC, Ltd, Company, Co
                clean_alias = re.sub(r"\b(inc|llc|ltd|company|co|corp|corporation|mfg|manufacturing)\b", "", norm_key, flags=re.IGNORECASE)
                clean_alias = re.sub(r"\s+", " ", clean_alias).strip()
                if clean_alias and clean_alias not in self.normalized_manuf_lookup:
                    self.normalized_manuf_lookup[clean_alias] = canonical_name

                if ref_code:
                    self.manuf_id_lookup[ref_code.lower()] = canonical_name

        # 2. Extract Brand Reference Data from input.csv feeds + Phase 2 output
        raw_brands: Set[str] = set()

        for col in ["E1_Brand", "DIB_Brand", "Unilog_Brand"]:
            if col in input_df.columns:
                for b_val in input_df[col].dropna().unique():
                    b_str = str(b_val).strip()
                    if b_str and not b_str.lower().startswith("--") and b_str.lower() not in ["null", "none", "nan", "unbranded"]:
                        raw_brands.add(b_str)

        # Load Phase 2 brand extractions
        try:
            p2_df = pd.read_csv(self.phase2_csv_path)
            if "brand" in p2_df.columns:
                for b_val in p2_df["brand"].dropna().unique():
                    b_str = str(b_val).strip()
                    if b_str and b_str.lower() not in ["null", "none", "nan"]:
                        raw_brands.add(b_str)
        except Exception:
            pass

        # Build Brand Reference Data with internal BRD_* IDs
        for brand_name in sorted(raw_brands):
            norm_b = self.normalize_key(brand_name)

            # Check if normalized brand matches existing canonical brand
            existing_canonical = self.normalized_brand_lookup.get(norm_b)
            if existing_canonical:
                canonical_brand = existing_canonical
            else:
                canonical_brand = brand_name
                # Create internal canonical brand ID
                clean_id_str = re.sub(r"[^\w]", "", brand_name.upper())
                brand_id = f"BRD_{clean_id_str}"
                self.brand_records[canonical_brand] = {
                    "canonical_name": canonical_brand,
                    "brand_id": brand_id
                }
                self.normalized_brand_lookup[norm_b] = canonical_brand
                self.brand_id_lookup[brand_id.lower()] = canonical_brand

        # 3. Build Manufacturer-Brand Relationships from input.csv + Phase 2
        try:
            combined_df = input_df.copy()
            p2_df = pd.read_csv(self.phase2_csv_path)
            if "brand" in p2_df.columns:
                combined_df["p2_brand"] = p2_df["brand"]

            for _, row in combined_df.iterrows():
                raw_pm = row.get("Part_Manuf")
                if pd.isna(raw_pm):
                    continue

                pm_match = re.search(r"^(.*?)\s*\(([^)]+)\)$", str(raw_pm).strip())
                manuf_name = pm_match.group(1).strip() if pm_match else str(raw_pm).strip()
                norm_m = self.normalize_key(manuf_name)
                canonical_m = self.normalized_manuf_lookup.get(norm_m)

                if not canonical_m:
                    continue

                # Check brand signals in this row
                b_signals = [row.get("E1_Brand"), row.get("DIB_Brand"), row.get("Unilog_Brand"), row.get("p2_brand")]
                for b_val in b_signals:
                    if pd.isna(b_val):
                        continue
                    b_str = str(b_val).strip()
                    if b_str and not b_str.lower().startswith("--") and b_str.lower() not in ["null", "none", "nan", "unbranded"]:
                        norm_b = self.normalize_key(b_str)
                        canonical_b = self.normalized_brand_lookup.get(norm_b)
                        if canonical_b:
                            if canonical_m not in self.manuf_to_brands:
                                self.manuf_to_brands[canonical_m] = set()
                            self.manuf_to_brands[canonical_m].add(canonical_b)

                            if canonical_b not in self.brand_to_manufs:
                                self.brand_to_manufs[canonical_b] = set()
                            self.brand_to_manufs[canonical_b].add(canonical_m)
        except Exception:
            pass

    def validate_relationship(self, manufacturer_canonical: Optional[str], brand_canonical: Optional[str]) -> bool:
        """
        Validates if the relationship between a canonical manufacturer and canonical brand exists
        in the derived reference data.
        """
        if not manufacturer_canonical or not brand_canonical:
            return False

        known_brands = self.manuf_to_brands.get(manufacturer_canonical, set())
        if brand_canonical in known_brands:
            return True

        known_manufs = self.brand_to_manufs.get(brand_canonical, set())
        if manufacturer_canonical in known_manufs:
            return True

        return False
