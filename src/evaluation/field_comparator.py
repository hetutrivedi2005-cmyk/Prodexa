import re
from typing import Any, Tuple


class FieldComparator:
    """
    Component 7 (Phase 15): Field-by-Field Comparator.
    Compares Prodexa values against expected Ground Truth reference values
    using strict normalization rules.
    """

    def normalize_value(self, val: Any) -> str:
        """
        Normalizes values to eliminate superficial formatting differences:
        - Lowercases
        - Trims whitespace
        - Unifies common unit variations (e.g., 'inches'/'inch' -> 'in', 'volts' -> 'v')
        """
        if val is None or str(val).strip() == "" or str(val).lower() == "nan" or str(val).lower() == "none":
            return ""

        s = str(val).strip().lower()
        # Remove quotes
        s = s.replace('"', '').replace("'", "")
        # Unit normalization
        s = re.sub(r'\b(?:inches|inch)\b', 'in', s)
        s = re.sub(r'\b(?:volts|volt)\b', 'v', s)
        s = re.sub(r'\b(?:watts|watt)\b', 'w', s)
        s = re.sub(r'\b(?:pack|pk|pcs|pc)\b', 'pcs', s)

        # Strip spaces around numbers and UOMs (e.g. '1/2 in' -> '1/2in')
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def compare_field(self, field_name: str, prodexa_val: Any, expected_val: Any) -> Tuple[str, str]:
        """
        Compares two values for a field.
        Returns a tuple of (status, mismatch_reason).
        Statuses: MATCH, MISMATCH, MISSING, EXTRA, NOT_APPLICABLE.
        """
        p_norm = self.normalize_value(prodexa_val)
        e_norm = self.normalize_value(expected_val)

        # If both are empty
        if not p_norm and not e_norm:
            return "NOT_APPLICABLE", ""

        # If expected has value, but Prodexa has none
        if e_norm and not p_norm:
            return "MISSING", "Expected value not populated in output"

        # If Prodexa has value, but expected has none
        if p_norm and not e_norm:
            return "EXTRA", "Prodexa populated extra attribute value"

        # If both have values, check for match
        if p_norm == e_norm:
            return "MATCH", ""

        return "MISMATCH", f"Value mismatch: got '{prodexa_val}', expected '{expected_val}'"
