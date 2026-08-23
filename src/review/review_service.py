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

    def get_review_queue(self, status_filter: Optional[str] = None, job_id: Optional[str] = None) -> List[ReviewItem]:
        items = list(self._items.values())
        if job_id:
            items = [i for i in items if i.job_id == job_id]
        if status_filter:
            items = [i for i in items if i.review_status == status_filter]
        return items

    def sync_job_review_items(self, job_id: str, results: List[dict]) -> List[ReviewItem]:
        synced = []
        for r in results:
            if r.get("status") == "NEEDS_REVIEW":
                p_id = r.get("product_id") or f"PROD-{job_id[-4:]}-{r.get('source_row_id', 1):04d}"
                attr_name = r.get("review_attribute") or "manufacturer"
                r_id = f"REV-{job_id[-4:]}-{r.get('source_row_id', 1):04d}"
                
                reason = r.get("review_reason") or "Low confidence on manufacturer grounding specification"
                conf = float(r.get("confidence", 0.68))
                prio = "HIGH" if conf < 0.70 else "MEDIUM"
                
                # Check if item already exists
                existing = self._items.get(r_id) or self._by_key.get((p_id, attr_name))
                if existing:
                    existing.job_id = job_id
                    existing.confidence_score = conf
                    existing.priority = prio
                    existing.review_comment = reason
                    synced.append(existing)
                else:
                    new_item = ReviewItem(
                        review_id=r_id,
                        job_id=job_id,
                        product_id=p_id,
                        attribute_name=attr_name,
                        current_value=r.get("brand") or r.get("manufacturer") or "Unassigned Brand",
                        proposed_value=r.get("manufacturer") or "Verified Manufacturer",
                        confidence_score=conf,
                        confidence_decision="REVIEW_RECOMMENDED",
                        validation_status="WARNING",
                        review_status="PENDING",
                        priority=prio,
                        review_comment=reason,
                        reason_codes=[reason],
                        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
                    )
                    self._items[new_item.review_id] = new_item
                    self._by_key[(p_id, attr_name)] = new_item
                    synced.append(new_item)
        return synced

    def _find_or_create_item(self, review_id: str) -> ReviewItem:
        # 1. Direct match by review_id
        if review_id in self._items:
            return self._items[review_id]

        # 2. Match by (product_id, attribute_name) tuple or colon key
        if ":" in review_id:
            parts = review_id.split(":", 1)
            p_id, a_name = parts[0].strip(), parts[1].strip()
            item = self._by_key.get((p_id, a_name))
            if item:
                return item
            for (p, a), it in self._by_key.items():
                if p.lower() == p_id.lower() and a.lower() == a_name.lower():
                    return it

        # 3. Match by item.product_id or item.review_key
        for it in self._items.values():
            if it.review_key == review_id or it.review_id == review_id or it.product_id == review_id:
                return it

        # 4. If key is formatted as PID:ATTR or single PID, dynamically create ReviewItem
        if ":" in review_id:
            parts = review_id.split(":", 1)
            p_id, a_name = parts[0].strip(), parts[1].strip()
        else:
            p_id, a_name = review_id.strip(), "attribute"

        new_item = ReviewItem(
            review_id=f"REV-{abs(hash(review_id)) % 1000000:06d}",
            product_id=p_id,
            attribute_name=a_name,
            current_value="",
            proposed_value="",
            confidence_score=0.50,
            confidence_decision="REVIEW_RECOMMENDED",
            validation_status="WARNING",
            review_status="PENDING",
            priority="MEDIUM",
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        self._items[new_item.review_id] = new_item
        self._by_key[(p_id, a_name)] = new_item
        return new_item

    def get_review_item(self, review_id: str) -> Optional[ReviewItem]:
        if review_id in self._items:
            return self._items[review_id]
        if ":" in review_id:
            parts = review_id.split(":", 1)
            item = self._by_key.get((parts[0].strip(), parts[1].strip()))
            if item:
                return item
        for it in self._items.values():
            if it.review_key == review_id or it.review_id == review_id:
                return it
        return None

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

    def approve_review(self, review_id: str, reviewer_id: str = "reviewer_default", comment: Optional[str] = None, force: bool = False) -> ReviewItem:
        item = self._find_or_create_item(review_id)
        if not force and item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")

        reason_text = (comment or "").strip() or "Verified and approved by reviewer based on manufacturer evidence."
        old_val = item.current_value or item.proposed_value
        item.previous_value = item.previous_value or old_val
        item.current_value = item.proposed_value or old_val
        item.review_status = "APPROVED"
        item.review_action = "ACCEPT"
        item.reviewer_id = reviewer_id
        item.review_comment = reason_text
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
            new_value=item.current_value,
            reviewer_id=reviewer_id,
            reason=reason_text,
            validation_result="PASS",
            confidence_before=item.confidence_score,
            confidence_after=1.00,
            evidence_id=item.evidence_id,
            source_id=item.source_id
        )
        self.audit_logger.log_action(rec)
        return item

    def edit_review(self, review_id: str, new_value: Any, reviewer_id: str = "reviewer_default", comment: Optional[str] = None, force: bool = False) -> ReviewItem:
        item = self._find_or_create_item(review_id)
        if not force and item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")

        reason_text = (comment or "").strip()
        if not reason_text:
            reason_text = f"Manual override: updated {item.attribute_name} to '{str(new_value).strip()}'."

        # Strict Validation Gate
        is_valid, err_msg = self.validate_human_edit(item.attribute_name, new_value)
        if not is_valid:
            raise ValueError(f"Edit rejected: {err_msg}")

        old_val = item.current_value or item.proposed_value
        item.previous_value = old_val
        item.current_value = str(new_value).strip()
        item.proposed_value = str(new_value).strip()
        item.review_status = "EDITED"
        item.review_action = "EDIT"
        item.reviewer_id = reviewer_id
        item.review_comment = reason_text
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
            reason=reason_text,
            validation_result="PASS",
            confidence_before=item.confidence_score,
            confidence_after=1.00,
            evidence_id=item.evidence_id,
            source_id=item.source_id
        )
        self.audit_logger.log_action(rec)
        return item

    def reject_review(self, review_id: str, reviewer_id: str = "reviewer_default", comment: Optional[str] = None, force: bool = False) -> ReviewItem:
        item = self._find_or_create_item(review_id)
        if not force and item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")
        if not comment or not comment.strip():
            raise ValueError("Rejection reason comment is required.")
        
        reason_text = comment.strip()

        old_val = item.current_value or item.proposed_value
        item.previous_value = old_val
        item.current_value = ""
        item.proposed_value = ""
        item.review_status = "REJECTED"
        item.review_action = "REJECT"
        item.reviewer_id = reviewer_id
        item.review_comment = reason_text
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
            new_value="",
            reviewer_id=reviewer_id,
            reason=reason_text,
            validation_result="REJECTED",
            confidence_before=item.confidence_score,
            confidence_after=0.00,
            evidence_id=item.evidence_id,
            source_id=item.source_id
        )
        self.audit_logger.log_action(rec)
        return item

    def escalate_review(self, review_id: str, reviewer_id: str = "reviewer_default", comment: Optional[str] = None, force: bool = False) -> ReviewItem:
        item = self._find_or_create_item(review_id)
        if not force and item.review_status in ["APPROVED", "EDITED", "REJECTED"]:
            raise ValueError(f"Review item '{review_id}' has already been resolved ({item.review_status}).")
        if not comment or not comment.strip():
            raise ValueError("Escalation reason comment is required.")
        
        reason_text = comment.strip()

        old_val = item.current_value or item.proposed_value
        item.previous_value = item.previous_value or old_val
        item.review_status = "ESCALATED"
        item.review_action = "ESCALATE"
        item.reviewer_id = reviewer_id
        item.review_comment = reason_text
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
            reason=reason_text,
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

review_service = ReviewService()
