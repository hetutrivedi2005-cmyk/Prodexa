import os
import re
import pandas as pd
from fractions import Fraction
from decimal import Decimal
from typing import Dict, List, Set, Any, Optional, Tuple


class UOMNormalizer:
    """
    100% Rule-Based, Deterministic UOM Normalization Engine.
    ZERO LLM / AI / Fuzzy matching / Semantic inference / Unit guessing.
    """

    ALLOWED_DENOMINATORS = {1, 2, 4, 8, 16, 32, 64}

    # Attributes that are explicitly defined as length/dimension measurements in inches
    INCH_DIMENSION_ATTRIBUTES = {
        "dimensions", "diameter", "length", "width", "height", "depth", "arbor_size", "drive_size"
    }

    # Non-measurement / pass-through attributes
    NON_MEASUREMENT_ATTRIBUTES = {
        "grit", "color_finish", "material", "target_material", "brand", "manufacturer"
    }

    def __init__(self, uom_master_path: str = "data/master/uom_master.csv"):
        self.uom_master_path = uom_master_path
        self.uom_alias_map: Dict[str, str] = {}
        self.canonical_uom_set: Set[str] = set()
        self._load_uom_master()

    def _load_uom_master(self):
        if not os.path.exists(self.uom_master_path):
            raise FileNotFoundError(f"Authoritative UOM Master not found at '{self.uom_master_path}'")

        df = pd.read_csv(self.uom_master_path)
        for _, row in df.iterrows():
            canon = str(row["canonical_uom"]).strip()
            self.canonical_uom_set.add(canon)
            self.uom_alias_map[canon.lower()] = canon

            aliases = str(row.get("aliases") or "").split(";")
            for a in aliases:
                a_clean = a.strip().lower()
                if a_clean:
                    self.uom_alias_map[a_clean] = canon

        # Pre-seed standard variations
        self.uom_alias_map["in."] = "in"
        self.uom_alias_map["inch"] = "in"
        self.uom_alias_map["inches"] = "in"
        self.uom_alias_map['"'] = "in"
        self.uom_alias_map["''"] = "in"

        self.uom_alias_map["mm."] = "mm"
        self.uom_alias_map["millimeter"] = "mm"
        self.uom_alias_map["millimeters"] = "mm"
        self.uom_alias_map["m.m."] = "mm"

        self.uom_alias_map["ft."] = "ft"
        self.uom_alias_map["foot"] = "ft"
        self.uom_alias_map["feet"] = "ft"
        self.uom_alias_map["'"] = "ft"

        self.uom_alias_map["volt"] = "V"
        self.uom_alias_map["volts"] = "V"

        self.uom_alias_map["watt"] = "W"
        self.uom_alias_map["watts"] = "W"

        self.uom_alias_map["amp hour"] = "Ah"
        self.uom_alias_map["amp-hours"] = "Ah"
        self.uom_alias_map["ah"] = "Ah"

        self.uom_alias_map["kelvin"] = "K"

        self.uom_alias_map["pc"] = "pcs"
        self.uom_alias_map["piece"] = "pcs"
        self.uom_alias_map["pieces"] = "pcs"

    def normalize(
        self,
        raw_value: Any,
        attribute_name: Optional[str] = None,
        category_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for deterministic UOM normalization.
        Returns a dict adhering to Phase 7 specification.
        """

        if raw_value is None or pd.isna(raw_value):
            return self._make_result(raw_value, None, None, "not_applicable", "not_applicable", 1.0)

        raw_str = str(raw_value).strip()
        if not raw_str or raw_str.upper() in ["UNKNOWN", "N/A", "--", "NONE", "NOT SPECIFIED", "UNAPPROVED_VALUE"]:
            return self._make_result(raw_str, None, None, "unsupported", "unresolved", 0.0)

        attr_clean = str(attribute_name).strip().lower() if attribute_name else ""

        # Non-measurement attributes (e.g. grit, color_finish) bypass normalization
        if attr_clean in self.NON_MEASUREMENT_ATTRIBUTES:
            return self._make_result(raw_str, raw_str, None, "already_canonical", "normalized", 1.0)

        # Handle compound dimension expressions (e.g. 1/2"x18", 2.75x30)
        if "x" in raw_str.lower() or "X" in raw_str:
            return self._parse_dimension_expression(raw_str, attr_clean, category_id)

        # Single measurement parsing
        return self._parse_single_measurement(raw_str, attr_clean, category_id)

    def _parse_dimension_expression(
        self,
        raw_str: str,
        attr_clean: str,
        category_id: Optional[str]
    ) -> Dict[str, Any]:
        parts = [p.strip() for p in re.split(r"[xX]", raw_str) if p.strip()]
        if len(parts) < 2:
            return self._make_result(raw_str, None, None, "unsupported_unit", "unresolved", 0.0)

        # Context check: Is unit established explicitly or by schema context?
        has_explicit_unit = any('"' in p or "'" in p or "in" in p.lower() or "mm" in p.lower() for p in parts)
        unit_established_by_context = (attr_clean in self.INCH_DIMENSION_ATTRIBUTES) or has_explicit_unit

        if not unit_established_by_context:
            # Deterministic safety rule: Do NOT guess missing units
            return self._make_result(raw_str, None, None, "unsupported_unit", "unresolved", 0.0)

        norm_parts = []
        target_unit = "in"  # Context establishes inches for industrial dimensions

        for part in parts:
            p_clean = re.sub(r'["\']', '', part).strip()
            # Strip trailing unit if present
            m_unit = re.match(r"^([\d./\s-]+)\s*([a-zA-Z]+)?$", p_clean)
            if m_unit:
                val_text = m_unit.group(1).strip()
                unit_text = m_unit.group(2)
                if unit_text and unit_text.lower() in self.uom_alias_map:
                    target_unit = self.uom_alias_map[unit_text.lower()]
            else:
                val_text = p_clean

            part_norm = self._convert_number_str(val_text)
            if part_norm is None:
                return self._make_result(raw_str, None, None, "unsupported_unit", "unresolved", 0.0)
            norm_parts.append(f"{part_norm} {target_unit}")

        canonical_val = " x ".join(norm_parts)

        # Determine specific transformation method
        method = "compound_dimension"
        if canonical_val == raw_str:
            method = "already_canonical"

        return self._make_result(raw_str, canonical_val, target_unit, method, "normalized", 1.0)

    def _parse_single_measurement(
        self,
        raw_str: str,
        attr_clean: str,
        category_id: Optional[str]
    ) -> Dict[str, Any]:
        # Handle unit-less numbers (e.g. pack_quantity = 6 or 6.0)
        if attr_clean in ["pack_quantity", "piece_count"]:
            try:
                f_val = float(raw_str)
                int_val = int(f_val) if f_val.is_integer() else f_val
                canon_str = str(int_val)
                method = "already_canonical" if canon_str == raw_str else "decimal_normalization"
                return self._make_result(raw_str, canon_str, "pcs", method, "normalized", 1.0)
            except ValueError:
                pass

        # Handle voltage, wattage, color_temp special formats (e.g. 20V -> 20 V, 60W -> 60 W, 27K -> 2700 K)
        if attr_clean == "voltage":
            m_v = re.match(r"^(\d+(?:\.\d+)?)\s*(V|volt|volts)?$", raw_str, re.I)
            if m_v:
                val_num = str(int(float(m_v.group(1)))) if float(m_v.group(1)).is_integer() else m_v.group(1)
                canon_val = f"{val_num} V"
                method = "already_canonical" if canon_val == raw_str else "unit_alias"
                return self._make_result(raw_str, canon_val, "V", method, "normalized", 1.0)

        if attr_clean == "wattage":
            m_w = re.match(r"^(\d+(?:\.\d+)?)\s*(W|watt|watts)?$", raw_str, re.I)
            if m_w:
                val_num = str(int(float(m_w.group(1)))) if float(m_w.group(1)).is_integer() else m_w.group(1)
                canon_val = f"{val_num} W"
                method = "already_canonical" if canon_val == raw_str else "unit_alias"
                return self._make_result(raw_str, canon_val, "W", method, "normalized", 1.0)

        if attr_clean == "color_temperature":
            m_k = re.match(r"^(\d+)\s*(K|kelvin)?$", raw_str, re.I)
            if m_k:
                k_num = int(m_k.group(1))
                if k_num < 100:
                    k_num *= 100
                canon_val = f"{k_num} K"
                method = "already_canonical" if canon_val == raw_str else "unit_alias"
                return self._make_result(raw_str, canon_val, "K", method, "normalized", 1.0)

        # Regex match for general number + unit string
        m = re.match(r"^([\d\s./-]+)\s*([a-zA-Z\"']+\.?|°[CK])?$", raw_str)
        if not m:
            return self._make_result(raw_str, None, None, "unsupported_unit", "unresolved", 0.0)

        val_text = m.group(1).strip()
        unit_text = m.group(2)

        # Detect Unit
        detected_unit = None
        if unit_text:
            u_clean = unit_text.strip().lower()
            if u_clean in self.uom_alias_map:
                detected_unit = self.uom_alias_map[u_clean]
            else:
                return self._make_result(raw_str, None, None, "unsupported_unit", "unresolved", 0.0)
        elif attr_clean in self.INCH_DIMENSION_ATTRIBUTES:
            detected_unit = "in"
        elif attr_clean == "grit":
            detected_unit = "Grit"

        # Convert number part
        norm_number, convert_method = self._convert_number_with_method(val_text)
        if norm_number is None:
            return self._make_result(raw_str, None, None, "unsupported_unit", "unresolved", 0.0)

        if detected_unit:
            canonical_val = f"{norm_number} {detected_unit}".strip()
        else:
            canonical_val = norm_number

        # Determine method tag
        if canonical_val == raw_str:
            method = "already_canonical"
        elif unit_text and unit_text.lower() != (detected_unit.lower() if detected_unit else ""):
            method = "unit_alias"
        else:
            method = convert_method

        return self._make_result(raw_str, canonical_val, detected_unit, method, "normalized", 1.0)

    def _convert_number_str(self, val_text: str) -> Optional[str]:
        res, _ = self._convert_number_with_method(val_text)
        return res

    def _convert_number_with_method(self, val_text: str) -> Tuple[Optional[str], str]:
        val_clean = val_text.strip()

        # Mixed Fraction (e.g. "1 1/2", "50-1/4", "2-3/8")
        m_mix = re.match(r"^(\d+)[-\s]+(\d+)/(\d+)$", val_clean)
        if m_mix:
            whole = int(m_mix.group(1))
            num = int(m_mix.group(2))
            den = int(m_mix.group(3))
            frac = Fraction(num, den)
            return f"{whole}-{frac.numerator}/{frac.denominator}", "mixed_fraction_normalization"

        # Simple Fraction (e.g. "1/2", "3/8")
        m_frac = re.match(r"^(\d+)/(\d+)$", val_clean)
        if m_frac:
            num = int(m_frac.group(1))
            den = int(m_frac.group(2))
            frac = Fraction(num, den)
            return f"{frac.numerator}/{frac.denominator}", "fraction_normalization"

        # Decimal or Integer
        try:
            f_val = float(val_clean)
            if f_val.is_integer():
                return str(int(f_val)), "decimal_normalization"

            # Convert decimal inch to fraction if denominator is valid
            frac_str = self._try_decimal_to_fraction(f_val)
            if frac_str:
                method = "mixed_fraction_normalization" if "-" in frac_str else "fraction_normalization"
                return frac_str, method

            return str(f_val), "decimal_normalization"
        except ValueError:
            return None, "unsupported"

    def _try_decimal_to_fraction(self, val_float: float) -> Optional[str]:
        int_part = int(val_float)
        rem = round(val_float - int_part, 6)

        if rem == 0:
            return str(int_part)

        frac = Fraction(rem).limit_denominator(64)
        if frac.denominator in self.ALLOWED_DENOMINATORS:
            if int_part > 0:
                return f"{int_part}-{frac.numerator}/{frac.denominator}"
            else:
                return f"{frac.numerator}/{frac.denominator}"

        return None

    def _make_result(
        self,
        raw_val: Any,
        norm_val: Optional[str],
        uom: Optional[str],
        method: str,
        status: str,
        confidence: float
    ) -> Dict[str, Any]:
        return {
            "raw_value": str(raw_val) if raw_val is not None else None,
            "normalized_value": norm_val,
            "uom": uom,
            "method": method,
            "status": status,
            "confidence": confidence
        }
