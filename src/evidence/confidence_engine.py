from typing import Tuple, Dict


class ConfidenceEngine:
    """
    Component 2 (Phase 9.1): Calibrated Confidence Engine.
    Calculates explainable factor breakdown dict + confidence band assignment:
    - HIGH: >= 0.95
    - MEDIUM: 0.85 - 0.9499
    - LOW: 0.70 - 0.8499
    - UNVERIFIED: < 0.70
    Enforces rule: Confidence NEVER overrides evidence validation failure.
    """

    def calculate_confidence(
        self,
        source_authority_score: float,
        mpn_verified: bool,
        manufacturer_verified: bool,
        evidence_grounded: bool,
        lov_valid: bool,
        uom_valid: bool,
        has_conflict: bool
    ) -> Tuple[float, Dict[str, float], str]:
        # Breakdown factors
        src_auth = max(0.0, min(1.0, float(source_authority_score)))
        mpn_score = 1.0 if mpn_verified else 0.0
        mfg_score = 1.0 if manufacturer_verified else 0.0
        ev_score = 1.0 if evidence_grounded else 0.0
        lov_score = 1.0 if lov_valid else 0.0
        uom_score = 1.0 if uom_valid else 0.0
        conflict_pen = 0.50 if has_conflict else 0.00

        # Weighted calculation:
        # source_authority * 0.25 + mpn_match * 0.25 + mfg_match * 0.20 + evidence_strength * 0.15 + lov_valid * 0.08 + uom_valid * 0.07 - conflict_penalty
        raw_conf = (
            src_auth * 0.25 +
            mpn_score * 0.25 +
            mfg_score * 0.20 +
            ev_score * 0.15 +
            lov_score * 0.08 +
            uom_score * 0.07 -
            conflict_pen
        )

        # Rule: Confidence NEVER overrides evidence grounding failure
        if not evidence_grounded or not mpn_verified or not manufacturer_verified:
            raw_conf = min(raw_conf, 0.40)

        final_conf = max(0.0, min(1.0, round(raw_conf, 4)))

        # Assign confidence band
        if final_conf >= 0.95:
            band = "HIGH"
        elif final_conf >= 0.85:
            band = "MEDIUM"
        elif final_conf >= 0.70:
            band = "LOW"
        else:
            band = "UNVERIFIED"

        breakdown = {
            "source_authority": round(src_auth, 4),
            "mpn_match": round(mpn_score, 4),
            "manufacturer_match": round(mfg_score, 4),
            "evidence_strength": round(ev_score, 4),
            "lov_validation": round(lov_score, 4),
            "uom_validation": round(uom_score, 4),
            "conflict_penalty": round(conflict_pen, 4),
            "final_confidence": final_conf,
            "confidence_band": band
        }

        return final_conf, breakdown, band
