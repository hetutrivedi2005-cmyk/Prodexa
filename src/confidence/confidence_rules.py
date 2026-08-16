from typing import Dict, Any, List, Optional, Tuple


SOURCE_AUTHORITY_SCORES = {
    "manufacturer_product_page": 1.00,
    "official_manufacturer_product_page": 1.00,
    "manufacturer_technical_pdf": 1.00,
    "official_manufacturer_technical_pdf": 1.00,
    "manufacturer_catalog": 0.95,
    "manufacturer_manual": 0.95,
    "official_manufacturer_documentation": 0.95,
    "authorized_technical_documentation": 0.80,
    "authorized_distributor_technical_page": 0.60,
    "distributor_product_page": 0.40,
    "marketplace": 0.00,
    "unknown": 0.00
}

SIGNAL_WEIGHTS = {
    "source_authority": 0.25,
    "evidence_grounding": 0.20,
    "extraction_quality": 0.20,
    "lov_compliance": 0.10,
    "uom_compliance": 0.10,
    "validation_score": 0.15
}


class ConfidenceRulesEngine:
    """
    Component 2 (Phase 11): Confidence Rules & Weight Engine.
    Implements deterministic, evidence-based quality scoring with dynamic weight renormalization
    and strict hard safety gates. Zero AI probabilities or score inflation.
    """

    def calculate_confidence(
        self,
        source_type: Optional[str],
        evidence_record: Optional[Dict[str, Any]],
        validation_record: Optional[Dict[str, Any]],
        is_lov_attr: bool,
        is_uom_attr: bool
    ) -> Tuple[float, int, str, Dict[str, Optional[float]], List[str]]:
        
        signals: Dict[str, Optional[float]] = {}
        reason_codes: List[str] = []

        # 1. Source Authority Signal
        clean_src_type = str(source_type or evidence_record.get("source_type") if evidence_record else "").lower().strip()
        if "manufacturer" in clean_src_type or "mfg" in clean_src_type:
            src_score = SOURCE_AUTHORITY_SCORES.get(clean_src_type, 1.00)
            reason_codes.append("OFFICIAL_MANUFACTURER_SOURCE")
            reason_codes.append("HIGH_AUTHORITY_SOURCE")
        elif "distributor" in clean_src_type:
            src_score = SOURCE_AUTHORITY_SCORES.get(clean_src_type, 0.50)
            reason_codes.append("AUTHORIZED_DISTRIBUTOR_SOURCE")
        elif "marketplace" in clean_src_type:
            src_score = 0.00
            reason_codes.append("LOW_AUTHORITY_SOURCE")
        elif clean_src_type:
            src_score = SOURCE_AUTHORITY_SCORES.get(clean_src_type, 0.50)
        else:
            src_score = 0.50
        signals["source_authority"] = src_score

        # 2. Evidence Grounding Signal
        if not evidence_record:
            if clean_src_type in ["baseline", "native_dataset", "initial_catalog"] or not source_type:
                ev_score = 1.00
                reason_codes.append("BASELINE_NATIVE_ATTRIBUTE")
                reason_codes.append("EVIDENCE_GROUNDED")
            else:
                ev_score = 0.00
                reason_codes.append("MISSING_EVIDENCE")
        else:
            has_text = bool(evidence_record.get("evidence_text"))
            is_grounded = evidence_record.get("status") in ["verified", "complete"]
            mpn_match = evidence_record.get("mpn_verified")
            mfg_match = evidence_record.get("manufacturer_verified")

            if mpn_match is False:
                reason_codes.append("MPN_MISMATCH")
            if mfg_match is False:
                reason_codes.append("MANUFACTURER_MISMATCH")

            if has_text and is_grounded and (mpn_match is not False) and (mfg_match is not False):
                ev_score = 1.00
                reason_codes.append("EVIDENCE_GROUNDED")
                reason_codes.append("EXACT_MPN_MATCH")
                reason_codes.append("MANUFACTURER_VERIFIED")
            elif has_text and is_grounded:
                ev_score = 0.70
                reason_codes.append("EVIDENCE_GROUNDED")
            elif has_text:
                ev_score = 0.40
                reason_codes.append("PARTIAL_EVIDENCE")
            else:
                ev_score = 0.00
                reason_codes.append("MISSING_EVIDENCE")
        signals["evidence_grounding"] = ev_score

        # 3. Extraction Quality Signal
        if evidence_record and "confidence" in evidence_record:
            ext_score = float(evidence_record["confidence"])
            reason_codes.append("DIRECT_SPECIFICATION_MATCH")
        else:
            ext_score = 0.90 if evidence_record else None
        signals["extraction_quality"] = ext_score

        # 4. LOV Compliance Signal
        if is_lov_attr:
            if evidence_record and evidence_record.get("lov_valid") is False:
                lov_score = 0.00
                reason_codes.append("LOV_INVALID")
            else:
                lov_score = 1.00
                reason_codes.append("LOV_VALID")
            signals["lov_compliance"] = lov_score
        else:
            signals["lov_compliance"] = None

        # 5. UOM Compliance Signal
        if is_uom_attr:
            if evidence_record and evidence_record.get("uom_valid") is False:
                uom_score = 0.00
                reason_codes.append("UOM_INVALID")
            else:
                uom_score = 1.00
                reason_codes.append("UOM_VALID")
            signals["uom_compliance"] = uom_score
        else:
            signals["uom_compliance"] = None

        # 6. Phase 10 Validation Signal
        if validation_record:
            v_status = validation_record.get("status", "PASS")
            if v_status == "PASS":
                val_score = 1.00
                reason_codes.append("VALIDATION_PASS")
            elif v_status == "PASS_WITH_WARNINGS" or v_status == "WARNING":
                val_score = 0.75
                reason_codes.append("VALIDATION_WARNING")
            else:
                val_score = 0.00
                reason_codes.append("VALIDATION_FAIL")
        else:
            val_score = 1.00
            reason_codes.append("VALIDATION_PASS")
        signals["validation_score"] = val_score

        # Check for Conflicts
        if evidence_record and (evidence_record.get("conflict_status") == "conflict" or evidence_record.get("manual_review_required")):
            reason_codes.append("CONFLICT_DETECTED")

        # Calculate Renormalized Weighted Sum
        active_weighted_sum = 0.0
        active_weight_total = 0.0

        for sig_name, sig_val in signals.items():
            if sig_val is not None:
                w = SIGNAL_WEIGHTS[sig_name]
                active_weighted_sum += sig_val * w
                active_weight_total += w

        if active_weight_total > 0.0:
            final_score = active_weighted_sum / active_weight_total
        else:
            final_score = 0.00

        final_score = max(0.00, min(1.00, round(final_score, 4)))
        percentage = int(round(final_score * 100))

        # Evaluate Thresholds & Hard Safety Gates
        if final_score >= 0.90:
            initial_decision = "AUTO_APPROVE"
        elif final_score >= 0.70:
            initial_decision = "REVIEW_RECOMMENDED"
        else:
            initial_decision = "HUMAN_REVIEW"

        # Apply Hard Safety Gates (Force HUMAN_REVIEW if safety fails)
        hard_gate_failed = (
            not evidence_record or
            signals["evidence_grounding"] == 0.00 or
            signals["source_authority"] == 0.00 or
            signals["validation_score"] == 0.00 or
            "LOW_AUTHORITY_SOURCE" in reason_codes or
            "MPN_MISMATCH" in reason_codes or
            "MANUFACTURER_MISMATCH" in reason_codes or
            "CONFLICT_DETECTED" in reason_codes or
            "LOV_INVALID" in reason_codes or
            "UOM_INVALID" in reason_codes or
            "MISSING_EVIDENCE" in reason_codes
        )

        if hard_gate_failed:
            decision = "HUMAN_REVIEW"
        else:
            decision = initial_decision

        return final_score, percentage, decision, signals, list(dict.fromkeys(reason_codes))
