from typing import Dict, Any
from src.evidence.evidence_model import EvidenceRecord


class EvidenceViewModelGenerator:
    """
    Component 6 (Phase 9.1): UI-Ready Evidence ViewModel Generator.
    Transforms evidence records into structured, frontend-ready view models matching Phase 9.1 UI schema:
    - attribute, value, status, confidence, confidence_band, validation, source, evidence.
    """

    def generate_view_model(self, record: EvidenceRecord) -> Dict[str, Any]:
        conf_band = record.confidence_breakdown.get("confidence_band") or (
            "HIGH" if record.confidence >= 0.95 else
            "MEDIUM" if record.confidence >= 0.85 else
            "LOW" if record.confidence >= 0.70 else "UNVERIFIED"
        )

        return {
            "attribute": record.attribute_name.replace("_", " ").title(),
            "value": str(record.value),
            "status": record.status,
            "confidence": record.confidence,
            "confidence_percent": int(round(record.confidence * 100)),
            "confidence_band": conf_band,
            "validation": {
                "source_verified": True,
                "mpn_verified": record.mpn_verified,
                "manufacturer_verified": record.manufacturer_verified,
                "lov_valid": record.lov_valid,
                "uom_valid": record.uom_valid,
                "grounded": record.validation_checks.get("evidence_text_nonempty", True),
                "normalized": record.normalized
            },
            "source": {
                "source_id": record.source_id,
                "source_type": record.source_type,
                "manufacturer": record.manufacturer,
                "url": record.source_url,
                "authority_score": record.source_authority_score
            },
            "evidence": {
                "text": record.evidence_text,
                "page": record.page_number,
                "section": record.section or record.evidence_location
            }
        }
