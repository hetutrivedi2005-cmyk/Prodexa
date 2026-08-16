from typing import Dict, Any, List
from src.confidence.confidence_model import AttributeConfidence


class ConfidenceExplainer:
    """
    Component 3 (Phase 11): Confidence Explainer Service.
    Generates human-readable breakdown text and UI explanations strictly titled 'Prodexa Confidence Score'.
    NEVER labels scores as 'AI Probability' or 'AI Confidence'.
    """

    def generate_explanation(self, conf: AttributeConfidence) -> str:
        pct = conf.confidence_percentage
        bar_len = int(pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        lines = [
            f"=== Prodexa Confidence Score: {conf.attribute_name} ===",
            f"Value: {conf.value}",
            f"Confidence Score: {pct}% [{bar}]",
            f"Decision: {conf.decision}",
            "",
            "Score Breakdown:",
            f"- Source Authority:      {int(round(conf.source_confidence * 100)) if conf.source_confidence is not None else 'N/A'}%"
            f" (Weight: 25%)",
            f"- Evidence Grounding:    {int(round(conf.evidence_confidence * 100)) if conf.evidence_confidence is not None else 'N/A'}%"
            f" (Weight: 20%)",
            f"- Extraction Quality:    {int(round(conf.extraction_confidence * 100)) if conf.extraction_confidence is not None else 'N/A'}%"
            f" (Weight: 20%)",
            f"- LOV Compliance:       {int(round(conf.lov_confidence * 100)) if conf.lov_confidence is not None else 'N/A'}%"
            f" (Weight: 10%)",
            f"- UOM Compliance:       {int(round(conf.uom_confidence * 100)) if conf.uom_confidence is not None else 'N/A'}%"
            f" (Weight: 10%)",
            f"- Phase 10 Validation:   {int(round(conf.validation_confidence * 100)) if conf.validation_confidence is not None else 'N/A'}%"
            f" (Weight: 15%)",
            "",
            "Reason Codes:"
        ]

        for rc in conf.reason_codes:
            lines.append(f"  ✓ {rc}")

        return "\n".join(lines)
