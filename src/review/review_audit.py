import os
import json
from typing import List, Optional
from src.review.review_model import ReviewAuditRecord


class ReviewAuditLogger:
    """
    Component 4 (Phase 12): Immutable Audit Logger.
    Appends append-only review decision audit records to data/review/review_audit.jsonl.
    """

    def __init__(self, audit_filepath: str = "data/review/review_audit.jsonl"):
        self.audit_filepath = audit_filepath

    def log_action(self, record: ReviewAuditRecord):
        os.makedirs(os.path.dirname(self.audit_filepath), exist_ok=True)
        with open(self.audit_filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def get_audit_history(self, product_id: Optional[str] = None) -> List[ReviewAuditRecord]:
        if not os.path.exists(self.audit_filepath):
            return []

        records = []
        with open(self.audit_filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    if product_id is None or d.get("product_id") == product_id:
                        rec = ReviewAuditRecord(
                            audit_id=d["audit_id"],
                            review_id=d["review_id"],
                            product_id=d["product_id"],
                            attribute_name=d["attribute_name"],
                            action=d["action"],
                            old_value=d["old_value"],
                            new_value=d["new_value"],
                            reviewer_id=d["reviewer_id"],
                            reason=d["reason"],
                            validation_result=d["validation_result"],
                            confidence_before=d["confidence_before"],
                            confidence_after=d["confidence_after"],
                            timestamp=d["timestamp"],
                            evidence_id=d.get("evidence_id"),
                            source_id=d.get("source_id")
                        )
                        records.append(rec)
        return records
