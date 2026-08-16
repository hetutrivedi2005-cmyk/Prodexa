from typing import List, Dict, Any, Optional, Tuple
from src.review.review_model import ReviewItem


class ReviewQueueEngine:
    """
    Component 2 (Phase 12): Review Queue Generator.
    Deterministically evaluates confidence, evidence, and validation signals to construct
    a prioritized human review queue.
    """

    def should_enter_queue(
        self,
        confidence_score: float,
        confidence_decision: str,
        validation_status: str,
        evidence_record: Optional[Dict[str, Any]],
        reason_codes: List[str]
    ) -> Tuple[bool, str, List[str]]:
        reasons = list(reason_codes)
        requires_review = False
        priority = "LOW"

        if validation_status == "FAIL":
            requires_review = True
            priority = "HIGH"
            if "VALIDATION_FAIL" not in reasons:
                reasons.append("VALIDATION_FAIL")

        if confidence_score < 0.70 or confidence_decision == "HUMAN_REVIEW":
            requires_review = True
            if priority != "HIGH":
                priority = "HIGH"
            if "LOW_CONFIDENCE" not in reasons:
                reasons.append("LOW_CONFIDENCE")

        if evidence_record and evidence_record.get("conflict_status") == "conflict":
            requires_review = True
            if priority != "HIGH":
                priority = "HIGH"
            if "CONFLICT_DETECTED" not in reasons:
                reasons.append("CONFLICT_DETECTED")

        if not evidence_record or evidence_record.get("status") == "missing" or "MISSING_EVIDENCE" in reasons:
            requires_review = True
            if priority == "LOW":
                priority = "MEDIUM"

        if evidence_record and (evidence_record.get("mpn_verified") is False or "MPN_MISMATCH" in reasons):
            requires_review = True
            priority = "HIGH"

        if evidence_record and (evidence_record.get("manufacturer_verified") is False or "MANUFACTURER_MISMATCH" in reasons):
            requires_review = True
            priority = "HIGH"

        if confidence_decision == "REVIEW_RECOMMENDED" or validation_status in ["PASS_WITH_WARNINGS", "WARNING"]:
            requires_review = True
            if priority == "LOW":
                priority = "MEDIUM"

        return requires_review, priority, list(dict.fromkeys(reasons))

    def generate_queue(
        self,
        confidence_records: List[Dict[str, Any]],
        evidence_map: Dict[Tuple[str, str], dict],
        validation_map: Dict[Tuple[str, str], dict]
    ) -> List[ReviewItem]:

        queue: List[ReviewItem] = []
        review_counter = 1

        for c_rec in confidence_records:
            pid = str(c_rec["product_id"]).strip()
            attr = str(c_rec["attribute_name"]).strip()
            val = c_rec.get("value")
            score = float(c_rec.get("confidence_score", 0.0))
            dec = str(c_rec.get("decision", "HUMAN_REVIEW"))

            ev_rec = evidence_map.get((pid, attr))
            val_rec = validation_map.get((pid, attr))
            val_status = val_rec.get("status", "PASS") if val_rec else "PASS"

            raw_reasons = c_rec.get("reason_codes") or []
            if isinstance(raw_reasons, str):
                raw_reasons = raw_reasons.split("|")

            needs_rev, priority, final_reasons = self.should_enter_queue(
                confidence_score=score,
                confidence_decision=dec,
                validation_status=val_status,
                evidence_record=ev_rec,
                reason_codes=raw_reasons
            )

            if needs_rev:
                rev_id = f"REV-{review_counter:06d}"
                review_counter += 1

                ev_id = ev_rec.get("evidence_id") if ev_rec else c_rec.get("evidence_id")
                src_id = ev_rec.get("source_id") if ev_rec else c_rec.get("source_id")
                src_url = ev_rec.get("source_url") if ev_rec else None
                ev_txt = ev_rec.get("evidence_text") if ev_rec else None

                item = ReviewItem(
                    review_id=rev_id,
                    product_id=pid,
                    attribute_name=attr,
                    current_value=val,
                    proposed_value=val,
                    confidence_score=score,
                    confidence_decision=dec,
                    validation_status=val_status,
                    review_status="PENDING",
                    priority=priority,
                    evidence_id=ev_id,
                    source_id=src_id,
                    source_url=src_url,
                    evidence_text=ev_txt,
                    reason_codes=final_reasons
                )
                queue.append(item)

        # Deterministic Priority Sort:
        # Priority order: HIGH (0), MEDIUM (1), LOW (2), then lowest confidence score first
        prio_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        queue.sort(key=lambda x: (prio_order.get(x.priority, 9), x.confidence_score, x.product_id, x.attribute_name))

        return queue
