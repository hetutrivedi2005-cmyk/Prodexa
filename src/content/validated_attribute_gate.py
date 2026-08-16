from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class VerifiedAttributePayload:
    """
    Component 1 (Phase 13): Verified Attribute Payload Model.
    Contains ONLY trusted, validated, and approved product attributes.
    Raw or unvalidated input MUST NOT enter generation context.
    """
    product_id: str
    brand: Optional[str] = None
    mpn: Optional[str] = None
    product_type: Optional[str] = None
    validated_attributes: Dict[str, Any] = field(default_factory=dict)
    attribute_provenance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    is_eligible: bool = True
    has_pending_review: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class ValidatedAttributeGate:
    """
    Component 1 (Phase 13): Validated Attribute Gate.
    Filters raw/processed product data against Phase 10 Validation, Phase 11 Confidence,
    and Phase 12 Human Review decisions to build a clean VerifiedAttributePayload.
    """

    def extract_payload(
        self,
        product_id: str,
        product_row: dict,
        conf_records: List[dict],
        evidence_map: Dict[Tuple[str, str], dict],
        val_map: Dict[Tuple[str, str], dict],
        review_map: Dict[Tuple[str, str], dict]
    ) -> VerifiedAttributePayload:

        pid = str(product_id).strip()

        # Extract Core Identity
        brand = str(product_row.get("resolved_brand") or product_row.get("brand") or "").strip() or None
        mpn = str(product_row.get("resolved_mpn") or product_row.get("mpn") or "").strip() or None
        prod_type = str(product_row.get("primary_category_name") or product_row.get("product_type") or "").strip() or None

        validated_attrs: Dict[str, Any] = {}
        provenance: Dict[str, Dict[str, Any]] = {}
        has_pending = False

        # 1. Core Identity Attributes (Brand, MPN, Product Type) if PASS in Phase 10
        val_brand = val_map.get((pid, "brand"))
        if val_brand and val_brand.get("status") in ["PASS", "PASS_WITH_WARNINGS"] and brand:
            validated_attrs["brand"] = brand
            provenance["brand"] = {"confidence": 1.0, "status": "PASS", "source": "native_trusted"}

        val_mpn = val_map.get((pid, "mpn")) or val_map.get((pid, "resolved_mpn"))
        if mpn and (not val_mpn or val_mpn.get("status") in ["PASS", "PASS_WITH_WARNINGS"]):
            validated_attrs["mpn"] = mpn
            provenance["mpn"] = {"confidence": 1.0, "status": "PASS", "source": "native_trusted"}

        if prod_type:
            validated_attrs["product_type"] = prod_type
            provenance["product_type"] = {"confidence": 1.0, "status": "PASS", "source": "taxonomy"}

        # Check if product is flagged pending human review in Phase 12 or Phase 11
        if product_row.get("human_review_status") == "REVIEW_REQUIRED" or product_row.get("confidence_status") == "HUMAN_REVIEW":
            has_pending = True

        # 2. Attribute-level Evaluation from Phase 11 & Phase 12
        for c_rec in conf_records:
            if str(c_rec.get("product_id")).strip() != pid:
                continue

            attr = str(c_rec.get("attribute_name")).strip()
            score = float(c_rec.get("confidence_score", 0.0))
            dec = str(c_rec.get("decision", "HUMAN_REVIEW"))

            ev_rec = evidence_map.get((pid, attr))
            val_rec = val_map.get((pid, attr))
            val_status = val_rec.get("status", "PASS") if val_rec else "PASS"
            rev_rec = review_map.get((pid, attr))

            if val_status == "FAIL":
                has_pending = True
                continue

            if ev_rec and ev_rec.get("conflict_status") == "conflict":
                has_pending = True
                continue

            # Check Phase 12 Human Review override
            if rev_rec:
                rev_status = rev_rec.get("review_status")
                rev_action = rev_rec.get("review_action")

                if rev_status == "REJECTED" or rev_action == "REJECT":
                    continue
                if rev_status in ["PENDING", "IN_REVIEW", "ESCALATED"]:
                    has_pending = True
                    continue

                if rev_status == "EDITED" or rev_action == "EDIT":
                    edited_val = rev_rec.get("proposed_value") or rev_rec.get("new_value")
                    if edited_val is not None and str(edited_val).strip() != "":
                        validated_attrs[attr] = str(edited_val).strip()
                        provenance[attr] = {
                            "confidence": 1.00,
                            "status": "PASS",
                            "decision": "HUMAN_EDITED",
                            "reviewer_id": rev_rec.get("reviewer_id")
                        }
                        continue

                if rev_status == "APPROVED" or rev_action == "ACCEPT":
                    val = rev_rec.get("proposed_value") or c_rec.get("value")
                    if val is not None and str(val).strip() != "":
                        validated_attrs[attr] = str(val).strip()
                        provenance[attr] = {
                            "confidence": 1.00,
                            "status": "PASS",
                            "decision": "HUMAN_APPROVED",
                            "reviewer_id": rev_rec.get("reviewer_id")
                        }
                        continue

            if dec == "HUMAN_REVIEW":
                has_pending = True
                continue

            # Auto-Approved attributes from Phase 11
            if dec == "AUTO_APPROVE" and score >= 0.70:
                val = c_rec.get("value")
                if val is not None and str(val).strip() != "":
                    validated_attrs[attr] = str(val).strip()
                    provenance[attr] = {
                        "confidence": score,
                        "status": val_status,
                        "decision": "AUTO_APPROVE",
                        "evidence_id": ev_rec.get("evidence_id") if ev_rec else None
                    }

        return VerifiedAttributePayload(
            product_id=pid,
            brand=brand,
            mpn=mpn,
            product_type=prod_type,
            is_eligible=(not has_pending),
            has_pending_review=has_pending,
            validated_attributes=validated_attrs,
            attribute_provenance=provenance
        )
