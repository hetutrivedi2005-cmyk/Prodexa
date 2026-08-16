from typing import Dict, Any, List, Optional, Tuple, Set


class FinalOutputGate:
    """
    Component 1 (Phase 14): Final Output Eligibility Gate.
    Determines whether a product and each of its attributes meet all the strict conditions
    required to enter the final trusted output, mapping exclusions to deterministic codes.
    """

    BASELINE_ATTRIBUTES: Set[str] = {
        "brand", "mpn", "manufacturer", "product_type", "size", "quantity",
        "dimensions", "pack_quantity"
    }

    def evaluate_product_eligibility(
        self,
        product_id: str,
        product_row: dict,
        desc_rec: Optional[dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates product-level constraints (Identity and Description).
        """
        pid = str(product_id).strip()

        # 1. Identity validation
        id_val_status = str(product_row.get("validation_status", "PASS")).strip()
        if "FAIL" in id_val_status or product_row.get("identity_valid") is False:
            return False, "IDENTITY_MISMATCH"

        # 2. Description validation
        if desc_rec:
            status = str(desc_rec.get("validation_status") or desc_rec.get("generation_status") or "FAIL").strip()
            if status != "PASS" and status != "VALIDATED":
                return False, "DESCRIPTION_VALIDATION_FAILED"
        else:
            # If description record is completely missing, fail
            return False, "DESCRIPTION_VALIDATION_FAILED"

        return True, None

    def evaluate_attribute_eligibility(
        self,
        product_id: str,
        attribute_name: str,
        value: Any,
        c_rec: Optional[dict],
        ev_rec: Optional[dict],
        val_rec: Optional[dict],
        rev_rec: Optional[dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines attribute-level eligibility with deterministic exclusion reasons.
        """
        pid = str(product_id).strip()
        attr = str(attribute_name).strip().lower()

        # 1. Check Phase 10 Validation
        val_status = str(val_rec.get("status") if val_rec else "PASS").strip()
        if val_status == "FAIL":
            return False, "VALIDATION_FAILED"

        # 2. Check Conflicts
        if ev_rec and str(ev_rec.get("conflict_status", "")).strip().lower() == "conflict":
            return False, "CONFLICT_DETECTED"

        # 3. Check Human Review Status / Decision
        if rev_rec:
            rev_status = str(rev_rec.get("review_status", "")).strip().upper()
            rev_action = str(rev_rec.get("review_action", "")).strip().upper()

            if rev_status == "REJECTED" or rev_action == "REJECT":
                return False, "ATTRIBUTE_REJECTED"

            if rev_status in ["PENDING", "IN_REVIEW", "ESCALATED"]:
                return False, "HUMAN_REVIEW_PENDING"

        # 4. Check Phase 11 Decision
        if c_rec:
            dec = str(c_rec.get("decision", "HUMAN_REVIEW")).strip().upper()
            score = float(c_rec.get("confidence_score", 0.0))

            if dec == "HUMAN_REVIEW" and not rev_rec:
                return False, "HUMAN_REVIEW_PENDING"

            if dec == "REJECTED":
                return False, "ATTRIBUTE_REJECTED"

        # 5. Check Evidence requirements
        is_baseline = attr in self.BASELINE_ATTRIBUTES

        if not is_baseline:
            # Enriched attributes MUST have valid evidence
            if not ev_rec:
                return False, "EVIDENCE_REQUIRED_MISSING"

            # Check verification status and grounding
            ev_status = str(ev_rec.get("evidence_status") or ev_rec.get("verification_status") or "").strip().lower()
            ev_conf = float(ev_rec.get("attribute_confidence") or ev_rec.get("confidence") or 0.0)

            if ev_status == "unverified" or ev_conf < 0.70:
                return False, "UNGROUNDED_EVIDENCE"

        return True, None
