from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import datetime

ALLOWED_DECISIONS = {"AUTO_APPROVE", "REVIEW_RECOMMENDED", "HUMAN_REVIEW"}


@dataclass
class AttributeConfidence:
    """
    Component 1 (Phase 11): Field-Level Confidence Model.
    Strict structured model representing the deterministic confidence score and breakdown of an attribute value.
    """
    product_id: str
    attribute_name: str
    value: Any
    confidence_score: float
    confidence_percentage: int
    decision: str
    source_confidence: Optional[float] = None
    evidence_confidence: Optional[float] = None
    extraction_confidence: Optional[float] = None
    lov_confidence: Optional[float] = None
    uom_confidence: Optional[float] = None
    validation_confidence: Optional[float] = None
    reason_codes: List[str] = field(default_factory=list)
    evidence_id: Optional[str] = None
    source_id: Optional[str] = None
    status: str = "verified"
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __post_init__(self):
        if not (0.00 <= round(self.confidence_score, 4) <= 1.00):
            raise ValueError(f"Confidence score {self.confidence_score} out of bounds [0.00, 1.00].")
        if self.decision not in ALLOWED_DECISIONS:
            raise ValueError(f"Invalid decision '{self.decision}'. Allowed: {ALLOWED_DECISIONS}")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["confidence_score"] = round(float(self.confidence_score), 4)
        return d
