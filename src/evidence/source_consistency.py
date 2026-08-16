import re
from typing import Dict, List, Any, Tuple


class SourceConsistencyEvaluator:
    """
    Component 3 (Phase 9.1): Source Consistency & Conflict Detector.
    Evaluates evidence records across multiple authoritative sources (e.g. PDF vs HTML).
    If sources disagree, records conflict_status = 'conflict' and manual_review_required = True.
    Never silently discards contradictory authoritative evidence.
    """

    def evaluate_consistency(self, evidence_records_for_attribute: List[Dict[str, Any]]) -> Tuple[str, bool, List[Dict[str, Any]]]:
        if not evidence_records_for_attribute or len(evidence_records_for_attribute) <= 1:
            return "consistent", False, evidence_records_for_attribute

        # Extract values
        values = []
        for r in evidence_records_for_attribute:
            val = r.get("value")
            if val is not None and str(val).strip():
                clean_v = re.sub(r"[^\w]", "", str(val).strip().lower())
                values.append(clean_v)

        if not values:
            return "consistent", False, evidence_records_for_attribute

        # Check if all normalized values match
        first_v = values[0]
        all_match = all(v == first_v for v in values)

        if all_match:
            return "consistent", False, evidence_records_for_attribute
        else:
            # Mark all records as conflict
            updated_records = []
            for r in evidence_records_for_attribute:
                r_copy = dict(r)
                r_copy["conflict_status"] = "conflict"
                r_copy["manual_review_required"] = True
                r_copy["status"] = "conflict"
                updated_records.append(r_copy)
            return "conflict", True, updated_records
