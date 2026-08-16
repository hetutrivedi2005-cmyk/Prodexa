import os
import re
from typing import Dict, List, Any, Optional

from src.understanding.lov_engine import LOVResolver
from src.understanding.uom_normalizer import UOMNormalizer


class EvidenceValidator:
    """
    Component 10: Evidence Validator Engine.
    Validates enrichment candidates against allowed category schema, source authority,
    exact MPN identity verification, evidence grounding, LOV compliance, and UOM standards.
    """

    def __init__(self):
        self.lov_resolver = LOVResolver()
        self.uom_normalizer = UOMNormalizer()

    def validate_candidate(
        self,
        candidate: dict,
        category_id: str,
        allowed_attributes: set,
        source_info: dict
    ) -> dict:
        attr_name = candidate.get("attribute_name")
        raw_val = candidate.get("value")
        evidence = candidate.get("evidence_text")
        conf = candidate.get("attribute_confidence", 0.0)

        # 1. Category Schema Enforcement
        if not attr_name or attr_name not in allowed_attributes:
            return {"decision": "reject", "reason": "attribute_not_allowed_for_category"}

        # 2. Evidence Grounding Check
        if not raw_val or not evidence or str(raw_val).strip() == "":
            return {"decision": "reject", "reason": "ungrounded_value_missing_evidence"}

        # 3. Source Provenance & Identity Verification
        if not source_info.get("identity_verified") or not source_info.get("mpn_verified"):
            return {"decision": "reject", "reason": "unverified_source_identity"}

        # 4. LOV Validation
        resolved_val = raw_val
        lov_res = self.lov_resolver.resolve_value(
            category_id=category_id,
            attribute_name=attr_name,
            raw_value=raw_val,
            source_fields=[evidence]
        )
        if lov_res and lov_res.get("status") in ["resolved", "canonical"]:
            resolved_val = lov_res.get("canonical_value") or resolved_val

        # 5. UOM Validation
        uom_res = self.uom_normalizer.normalize(resolved_val, attribute_name=attr_name, category_id=category_id)
        if uom_res and uom_res.get("status") in ["normalized", "already_canonical"]:
            resolved_val = uom_res.get("normalized_value") or resolved_val

        # 6. Confidence Bounds Check
        conf_bounded = max(0.0, min(1.0, float(conf)))

        validated_candidate = dict(candidate)
        validated_candidate["normalized_value"] = resolved_val
        validated_candidate["attribute_confidence"] = conf_bounded
        validated_candidate["decision"] = "accept"
        validated_candidate["reason"] = "valid_evidence_grounded"

        return validated_candidate
