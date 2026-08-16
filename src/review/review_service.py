import os
import json
import datetime
from typing import Dict, List, Optional, Any, Tuple

from src.review.review_model import ReviewItem, ReviewAuditRecord
from src.review.review_queue import ReviewQueueEngine
from src.review.review_audit import ReviewAuditLogger
from src.validation.character_limits import CharacterLimitValidator


LOV_GOVERNED_ATTRIBUTES = {"material", "color_finish", "color_temperature", "pack_quantity", "grit"}
UOM_GOVERNED_ATTRIBUTES = {"dimensions", "belt_dimensions", "length", "width_profile", "diameter", "arbor_size", "drive_size", "voltage", "wattage"}


class ReviewService:
    """
    Component 3 (Phase 12): Backend Review Service.
    Enforces review workflow state transitions, strict validation gates on human edits,
    and immutable audit logging.
    """

    def __init__(
        self,
        audit_filepath: str = "data/review/review_audit.jsonl",
        lov_csv_path: str = "data/master/attribute_lov.csv",
        uom_csv_path: str = "data/master/uom_master.csv"
    ):
        self.audit_logger = ReviewAuditLogger(audit_filepath)
        self.char_validator = CharacterLimitValidator()
        self._items: Dict[str, ReviewItem] = {}
        self._by_key: Dict[Tuple[str, str], ReviewItem] = {}
        self.audit_counter = 1

        # Load Approved LOVs
        self.approved_lovs: Dict[str, set] = {}
        if os.path.exists(lov_csv_path):
            import pandas as pd
            df_lov = pd.read_csv(lov_csv_path)
            for _, r in df_lov.iterrows():
                attr = str(r.get("attribute_name", "")).strip()
                if not attr:
                    continue
                c_val = str(r.get("canonical_value", "")).strip().lower()
                n_val = str(r.get("normalized_value", "")).strip().lower()
                aliases = str(r.get("aliases", "")).strip().lower().split(";") if not pd.isna(r.get("aliases")) else []
                
                s = self.approved_lovs.setdefault(attr, set())
                if c_val: s.add(c_val)
                if n_val: s.add(n_val)
                for a in aliases:
                    if a.strip(): s.add(a.strip())

        # Load Approved UOMs
        self.approved_uoms: set = set()
        if os.path.exists(uom_csv_path):
            import pandas as pd
            df_uom = pd.read_csv(uom_csv_path)
            for _, r in df_uom.iterrows():
                c_unit = str(r.get("canonical_uom", "")).strip().lower()
                n_unit = str(r.get("normalized_uom", "")).strip().lower()
                aliases = str(r.get("aliases", "")).strip().lower().split(";") if not pd.isna(r.get("aliases")) else []
                
                if c_unit: self.approved_uoms.add(c_unit)
                if n_unit: self.approved_uoms.add(n_unit)
                for a in aliases:
                    if a.strip(): self.approved_uoms.add(a.strip())

    def load_queue(self, queue: List[ReviewItem]):
        for item in queue:
            self._items[item.review_id] = item
            self._by_key[(item.product_id, item.attribute_name)] = item

    def get_review_queue(self, status_filter: Optional[str] = None) -> List[ReviewItem]:
        items = list(self._items.values())
        if status_filter:
            items = [i for i in items if i.review_status == status_filter]
        return items

    def get_review_item(self, review_id: str) -> Optional[ReviewItem]:
        return self._items.get(review_id)

    def get_product_review(self, product_id: str) -> List[ReviewItem]:
        return [i for i in self._items.values() if i.product_id == product_id]

    def get_attribute_review(self, product_id: str, attribute_name: str) -> Optional[ReviewItem]:
        return self._by_key.get((product_id, attribute_name))

    def validate_human_edit(self, attribute_name: str, new_value: Any) -> Tuple[bool, str]:
        if new_value is None or str(new_value).strip() == "":
            return False, f"Attribute '{attribute_name}' edit value cannot be empty."

        clean_val = str(new_value).strip()

        # 1. Character Limit Check
        res_char = self.char_validator.validate_field("EDIT", attribute_name, clean_val)
        if res_char.status == "FAIL":
            return False, res_char.message

        # 2. LOV Validation
        if attribute_name in LOV_GOVERNED_ATTRIBUTES:
            allowed = self.approved_lovs.get(attribute_name, set())
            if allowed and clean_val.lower() not in allowed:
                return False, f"Value '{clean_val}' is not present in attribute_lov.csv for '{attribute_name}'."

        # 3. UOM Validation
        if attribute_name in UOM_GOVERNED_ATTRIBUTES:
            unit_part = clean_val.split()[-1].lower() if len(clean_val.split()) > 1 else clean_val.lower()
            if self.approved_uoms and unit_part not in self.approved_uoms and clean_val.lower() not in self.approved_uoms:
                return False, f"Value '{clean_val}' contains unsupported UOM unit for '{attribute_name}'."

        return True, "PASS"

    def approve_review(self, review_id: str, reviewer_id: str = "reviewer_default", comment: Optional[str] = None) -> ReviewItem:
        item = self._items.get(review_id)
        if not item:
            raise KeyError(f"Review item '{review_id}' not found.")
        if item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")

        old_val = item.proposed_value
        item.review_status = "APPROVED"
        item.review_action = "ACCEPT"
        item.reviewer_id = reviewer_id
        item.review_comment = comment or "Evidence reviewed and accepted."
        item.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        item.resolved_at = item.updated_at

        # Log Audit Record
        audit_id = f"AUD-{self.audit_counter:06d}"
        self.audit_counter += 1
        rec = ReviewAuditRecord(
            audit_id=audit_id,
            review_id=review_id,
            product_id=item.product_id,
            attribute_name=item.attribute_name,
            action="ACCEPT",
            old_value=old_val,
            new_value=old_val,
            reviewer_id=reviewer_id,
            reason=item.review_comment,
            validation_result="PASS",
            confidence_before=item.confidence_score,
            confidence_after=1.00,
            evidence_id=item.evidence_id,
            source_id=item.source_id
        )
        self.audit_logger.log_action(rec)
        return item

    def edit_review(self, review_id: str, new_value: Any, reviewer_id: str = "reviewer_default", comment: Optional[str] = None) -> ReviewItem:
        item = self._items.get(review_id)
        if not item:
            raise KeyError(f"Review item '{review_id}' not found.")
        if item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")

        # Strict Validation Gate
        is_valid, err_msg = self.validate_human_edit(item.attribute_name, new_value)
        if not is_valid:
            raise ValueError(f"Edit rejected: {err_msg}")

        old_val = item.proposed_value
        item.proposed_value = str(new_value).strip()
        item.review_status = "EDITED"
        item.review_action = "EDIT"
        item.reviewer_id = reviewer_id
        item.review_comment = comment or f"Value edited to '{item.proposed_value}' by human reviewer."
        item.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        item.resolved_at = item.updated_at

        # Log Audit Record
        audit_id = f"AUD-{self.audit_counter:06d}"
        self.audit_counter += 1
        rec = ReviewAuditRecord(
            audit_id=audit_id,
            review_id=review_id,
            product_id=item.product_id,
            attribute_name=item.attribute_name,
            action="EDIT",
            old_value=old_val,
            new_value=item.proposed_value,
            reviewer_id=reviewer_id,
            reason=item.review_comment,
            validation_result="PASS",
            confidence_before=item.confidence_score,
            confidence_after=1.00,
            evidence_id=item.evidence_id,
            source_id=item.source_id
        )
        self.audit_logger.log_action(rec)
        return item

    def reject_review(self, review_id: str, reviewer_id: str = "reviewer_default", comment: Optional[str] = None) -> ReviewItem:
        item = self._items.get(review_id)
        if not item:
            raise KeyError(f"Review item '{review_id}' not found.")
        if item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")
        if not comment or not comment.strip():
            raise ValueError("Rejection reason comment is required.")

        old_val = item.proposed_value
        item.review_status = "REJECTED"
        item.review_action = "REJECT"
        item.reviewer_id = reviewer_id
        item.review_comment = comment.strip()
        item.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        item.resolved_at = item.updated_at

        # Log Audit Record
        audit_id = f"AUD-{self.audit_counter:06d}"
        self.audit_counter += 1
        rec = ReviewAuditRecord(
            audit_id=audit_id,
            review_id=review_id,
            product_id=item.product_id,
            attribute_name=item.attribute_name,
            action="REJECT",
            old_value=old_val,
            new_value=old_val,
            reviewer_id=reviewer_id,
            reason=item.review_comment,
            validation_result="REJECTED",
            confidence_before=item.confidence_score,
            confidence_after=0.00,
            evidence_id=item.evidence_id,
            source_id=item.source_id
        )
        self.audit_logger.log_action(rec)
        return item

    def escalate_review(self, review_id: str, reviewer_id: str = "reviewer_default", comment: Optional[str] = None) -> ReviewItem:
        item = self._items.get(review_id)
        if not item:
            raise KeyError(f"Review item '{review_id}' not found.")
        if item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")
        if not comment or not comment.strip():
            raise ValueError("Escalation reason comment is required.")

        old_val = item.proposed_value
        item.review_status = "ESCALATED"
        item.review_action = "ESCALATE"
        item.reviewer_id = reviewer_id
        item.review_comment = comment.strip()
        item.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Log Audit Record
        audit_id = f"AUD-{self.audit_counter:06d}"
        self.audit_counter += 1
        rec = ReviewAuditRecord(
            audit_id=audit_id,
            review_id=review_id,
            product_id=item.product_id,
            attribute_name=item.attribute_name,
            action="ESCALATE",
            old_value=old_val,
            new_value=old_val,
            reviewer_id=reviewer_id,
            reason=item.review_comment,
            validation_result="ESCALATED",
            confidence_before=item.confidence_score,
            confidence_after=item.confidence_score,
            evidence_id=item.evidence_id,
            source_id=item.source_id
        )
        self.audit_logger.log_action(rec)
        return item

    def get_review_history(self, product_id: Optional[str] = None) -> List[ReviewAuditRecord]:
        return self.audit_logger.get_audit_history(product_id)

    def get_review_statistics(self) -> Dict[str, Any]:
        all_items = list(self._items.values())
        tot = len(all_items)
        pending = sum(1 for i in all_items if i.review_status == "PENDING")
        in_rev = sum(1 for i in all_items if i.review_status == "IN_REVIEW")
        approved = sum(1 for i in all_items if i.review_status == "APPROVED")
        edited = sum(1 for i in all_items if i.review_status == "EDITED")
        rejected = sum(1 for i in all_items if i.review_status == "REJECTED")
        escalated = sum(1 for i in all_items if i.review_status == "ESCALATED")

        reviewed = approved + edited + rejected

        return {
            "total_items": tot,
            "pending_reviews": pending,
            "in_review": in_rev,
            "approved": approved,
            "edited": edited,
            "rejected": rejected,
            "escalated": escalated,
            "reviewed_total": reviewed,
            "acceptance_rate": round(approved / tot * 100, 2) if tot > 0 else 0.0,
            "edit_rate": round(edited / tot * 100, 2) if tot > 0 else 0.0,
            "rejection_rate": round(rejected / tot * 100, 2) if tot > 0 else 0.0,
            "escalation_rate": round(escalated / tot * 100, 2) if tot > 0 else 0.0
        }
