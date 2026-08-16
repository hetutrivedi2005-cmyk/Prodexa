from dataclasses import dataclass, field, asdict
from typing import Any, Optional
import datetime


ALLOWED_STATUSES = {"PASS", "WARNING", "FAIL", "NOT_APPLICABLE"}
ALLOWED_SEVERITIES = {"INFO", "WARNING", "ERROR"}


@dataclass
class ValidationResult:
    """
    Component 1 (Phase 10): Validation Result Data Model.
    Strict structured model representing the outcome of a single validation rule check.
    """
    validation_id: str
    product_id: str
    attribute_name: str
    rule_name: str
    status: str
    severity: str
    message: str
    expected: Any = None
    actual: Any = None
    source_id: Optional[str] = None
    evidence_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __post_init__(self):
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status '{self.status}'. Allowed statuses: {ALLOWED_STATUSES}")
        if self.severity not in ALLOWED_SEVERITIES:
            raise ValueError(f"Invalid severity '{self.severity}'. Allowed severities: {ALLOWED_SEVERITIES}")

    def to_dict(self) -> dict:
        return asdict(self)
