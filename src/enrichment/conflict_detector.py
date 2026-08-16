import re
from typing import Dict, Any, Tuple, Optional


class ConflictDetector:
    """
    Component 11: Conflict Detection Engine.
    Protects existing trusted Phase 7 product values. If authoritative source evidence
    disagrees with an existing trusted value, flags a conflict and requires manual review
    WITHOUT silently overwriting the trusted data.
    """

    def check_conflict(
        self,
        attribute_name: str,
        existing_val: Any,
        candidate_val: Any
    ) -> Tuple[bool, str]:
        """
        Returns (has_conflict, resolution_action).
        Actions: 'keep_existing', 'add_missing', 'conflict'
        """
        if existing_val is None or str(existing_val).strip() in ["", "None", "null", "nan"]:
            return False, "add_missing"

        clean_ext = self._normalize_comparable_string(existing_val)
        clean_cand = self._normalize_comparable_string(candidate_val)

        if clean_ext == clean_cand:
            return False, "keep_existing"
        else:
            return True, "conflict"

    def _normalize_comparable_string(self, val: Any) -> str:
        if val is None:
            return ""
        s = str(val).strip().lower()
        s = re.sub(r"\s+", " ", s)
        s = re.sub(r"[^\w\/\.\-]", "", s)
        return s
