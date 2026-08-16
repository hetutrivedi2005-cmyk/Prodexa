from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import datetime


ALLOWED_STATUSES = {"verified", "partially_verified", "unverified", "conflict", "rejected"}


@dataclass
class EvidenceRecord:
    """
    Component 1 (Phase 9): Evidence Record Data Model.
    Strict audit-ready model representing complete attribute-level provenance.
    """
    evidence_id: str
    product_id: str
    attribute_name: str
    value: Any

    source_id: str
    source_url: str
    source_type: str
    source_title: str

    manufacturer: str
    manufacturer_domain: str
    mpn: str
    normalized_mpn: str

    evidence_text: str
    evidence_location: str
    page_number: Optional[int]
    section: str

    source_authority_score: float

    mpn_verified: bool
    manufacturer_verified: bool
    lov_valid: bool
    uom_valid: bool
    normalized: bool

    validation_checks: Dict[str, bool] = field(default_factory=dict)

    confidence: float = 0.0
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)

    conflict_status: str = "none"
    manual_review_required: bool = False
    status: str = "unverified"
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __post_init__(self):
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status '{self.status}'. Allowed statuses: {ALLOWED_STATUSES}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Invalid confidence '{self.confidence}'. Must be between 0.0 and 1.0.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_ui_view_model(self) -> Dict[str, Any]:
        return {
            "attribute": self.attribute_name.replace("_", " ").title(),
            "value": str(self.value),
            "status": self.status,
            "confidence": self.confidence,
            "confidence_percent": int(round(self.confidence * 100)),
            "source": {
                "source_id": self.source_id,
                "name": self.source_title or self.source_type.replace("_", " ").title(),
                "url": self.source_url,
                "type": self.source_type,
                "manufacturer": self.manufacturer,
                "domain": self.manufacturer_domain,
                "authority_score": self.source_authority_score
            },
            "validation": {
                "lov_valid": self.lov_valid,
                "uom_valid": self.uom_valid,
                "mpn_verified": self.mpn_verified,
                "manufacturer_verified": self.manufacturer_verified,
                "normalized": self.normalized
            },
            "evidence": {
                "text": self.evidence_text,
                "location": self.evidence_location or self.section,
                "page": self.page_number,
                "section": self.section,
                "mpn": self.mpn,
                "normalized_mpn": self.normalized_mpn
            }
        }
