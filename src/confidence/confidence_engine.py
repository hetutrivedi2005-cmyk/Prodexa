from typing import Dict, List, Any, Optional, Tuple
from src.confidence.confidence_model import AttributeConfidence
from src.confidence.confidence_rules import ConfidenceRulesEngine
from src.confidence.confidence_explainer import ConfidenceExplainer


LOV_GOVERNED_ATTRIBUTES = {"material", "color_finish", "color_temperature", "pack_quantity", "grit"}
UOM_GOVERNED_ATTRIBUTES = {"dimensions", "belt_dimensions", "length", "width_profile", "diameter", "arbor_size", "drive_size", "voltage", "wattage"}


class ConfidenceEngine:
    """
    Component 3 (Phase 11): Core Confidence Engine.
    Evaluates attribute-level and product-level quality confidence scores deterministically.
    """

    def __init__(self):
        self.rules_engine = ConfidenceRulesEngine()
        self.explainer = ConfidenceExplainer()

    def evaluate_attribute(
        self,
        product_id: str,
        attribute_name: str,
        value: Any,
        source_type: Optional[str] = None,
        evidence_record: Optional[Dict[str, Any]] = None,
        validation_record: Optional[Dict[str, Any]] = None
    ) -> AttributeConfidence:

        is_lov = attribute_name in LOV_GOVERNED_ATTRIBUTES
        is_uom = attribute_name in UOM_GOVERNED_ATTRIBUTES

        score, pct, decision, signals, reasons = self.rules_engine.calculate_confidence(
            source_type=source_type,
            evidence_record=evidence_record,
            validation_record=validation_record,
            is_lov_attr=is_lov,
            is_uom_attr=is_uom
        )

        ev_id = evidence_record.get("evidence_id") if evidence_record else None
        src_id = evidence_record.get("source_id") if evidence_record else None
        st = evidence_record.get("status", "verified") if evidence_record else "unverified"

        return AttributeConfidence(
            product_id=product_id,
            attribute_name=attribute_name,
            value=value,
            confidence_score=score,
            confidence_percentage=pct,
            decision=decision,
            source_confidence=signals.get("source_authority"),
            evidence_confidence=signals.get("evidence_grounding"),
            extraction_confidence=signals.get("extraction_quality"),
            lov_confidence=signals.get("lov_compliance"),
            uom_confidence=signals.get("uom_compliance"),
            validation_confidence=signals.get("validation_score"),
            reason_codes=reasons,
            evidence_id=ev_id,
            source_id=src_id,
            status=st
        )

    def evaluate_product(
        self,
        product_id: str,
        attribute_confidences: List[AttributeConfidence],
        required_attribute_names: Optional[List[str]] = None
    ) -> Tuple[float, float, int, int, int]:
        """
        Calculates product-level metrics:
        - Lowest confidence score across required/all attributes (conservative quality gate)
        - Average confidence score
        - Counts for AUTO_APPROVE, REVIEW_RECOMMENDED, HUMAN_REVIEW
        """
        if not attribute_confidences:
            return 0.00, 0.00, 0, 0, 0

        auto_cnt = sum(1 for c in attribute_confidences if c.decision == "AUTO_APPROVE")
        rec_cnt = sum(1 for c in attribute_confidences if c.decision == "REVIEW_RECOMMENDED")
        rev_cnt = sum(1 for c in attribute_confidences if c.decision == "HUMAN_REVIEW")

        avg_score = round(sum(c.confidence_score for c in attribute_confidences) / len(attribute_confidences), 4)

        if required_attribute_names:
            req_confs = [c for c in attribute_confidences if c.attribute_name in required_attribute_names]
            if req_confs:
                min_score = min(c.confidence_score for c in req_confs)
            else:
                min_score = min(c.confidence_score for c in attribute_confidences)
        else:
            min_score = min(c.confidence_score for c in attribute_confidences)

        return min_score, avg_score, auto_cnt, rec_cnt, rev_cnt
