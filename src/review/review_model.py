from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import datetime

ALLOWED_REVIEW_STATUSES = {"PENDING", "IN_REVIEW", "APPROVED", "EDITED", "REJECTED", "ESCALATED"}
ALLOWED_REVIEW_ACTIONS = {"ACCEPT", "EDIT", "REJECT", "ESCALATE"}
ALLOWED_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}


@dataclass
class ReviewItem:
    """
    Component 1 (Phase 12): Human Review Item Model.
    Strict structured model representing a pending or resolved human review item.
    """
    review_id: str
    product_id: str
    attribute_name: str
    current_value: Any
    proposed_value: Any
    confidence_score: float
    confidence_decision: str
    validation_status: str
    review_status: str = "PENDING"
    priority: str = "HIGH"
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_action: Optional[str] = None
    review_comment: Optional[str] = None
    evidence_id: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    evidence_text: Optional[str] = None
    reason_codes: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    resolved_at: Optional[str] = None

    def __post_init__(self):
        if self.review_status not in ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"Invalid review_status '{self.review_status}'. Allowed: {ALLOWED_REVIEW_STATUSES}")
        if self.review_action and self.review_action not in ALLOWED_REVIEW_ACTIONS:
            raise ValueError(f"Invalid review_action '{self.review_action}'. Allowed: {ALLOWED_REVIEW_ACTIONS}")
        if self.priority not in ALLOWED_PRIORITIES:
            raise ValueError(f"Invalid priority '{self.priority}'. Allowed: {ALLOWED_PRIORITIES}")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReviewAuditRecord:
    """
    Component 1 (Phase 12): Immutable Audit Trail Model.
    """
    audit_id: str
    review_id: str
    product_id: str
    attribute_name: str
    action: str
    old_value: Any
    new_value: Any
    reviewer_id: str
    reason: str
    validation_result: str
    confidence_before: float
    confidence_after: float
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    evidence_id: Optional[str] = None
    source_id: Optional[str] = None

    def __post_init__(self):
        if self.action not in ALLOWED_REVIEW_ACTIONS:
            raise ValueError(f"Invalid audit action '{self.action}'. Allowed: {ALLOWED_REVIEW_ACTIONS}")

    def to_dict(self) -> dict:
        return asdict(self)
