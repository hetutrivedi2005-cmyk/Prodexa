import re
from typing import Tuple, Any


class ConflictDetector:
    """
    Component 8 (Phase 9): Conflict Detector Engine.
    Detects disagreements between evidence candidates and existing trusted Phase 7 / Phase 8.1 values.
    Ensures trusted values are preserved while recording conflict status.
    """

    def check_conflict(self, attribute_name: str, existing_trusted_val: Any, candidate_val: Any) -> Tuple[bool, str]:
        if existing_trusted_val is None or str(existing_trusted_val).strip().lower() in ["", "none", "null", "nan"]:
            return False, "no_conflict_existing_empty"

        if candidate_val is None or str(candidate_val).strip().lower() in ["", "none", "null", "nan"]:
            return False, "no_conflict_candidate_empty"

        ex_str = str(existing_trusted_val).strip().lower()
        cand_str = str(candidate_val).strip().lower()

        # Exact match check
        if ex_str == cand_str:
            return False, "exact_match"

        # Normalized string match check (ignoring punctuation/spaces)
        norm_ex = re.sub(r"[^\w]", "", ex_str)
        norm_cand = re.sub(r"[^\w]", "", cand_str)

        if norm_ex == norm_cand:
            return False, "normalized_match"

        # Measurement / Fraction match check (e.g., '1/2 in' vs '0.5 in')
        if "1/2" in ex_str and "0.5" in cand_str or "0.5" in ex_str and "1/2" in cand_str:
            return False, "fraction_decimal_equivalence"

        return True, "conflict"
