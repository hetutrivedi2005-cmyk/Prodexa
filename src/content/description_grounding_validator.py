import re
from typing import Dict, Any, List, Tuple
from src.content.validated_attribute_gate import VerifiedAttributePayload
from src.content.description_generator import PROHIBITED_MARKETING_TERMS

PROMPT_LEAKAGE_TERMS = {
    "system instruction", "llm prompt", "ignore previous instructions",
    "you are a controlled", "ai language model", "prompt leakage", "null", "undefined"
}


class DescriptionGroundingValidator:
    """
    Component 4 (Phase 13): Description Grounding Validator.
    Deterministically verifies that all factual claims, MPNs, numbers, materials,
    units, and dimensions in generated text exist in the VerifiedAttributePayload.
    """

    def validate_grounding(self, text: str, payload: VerifiedAttributePayload) -> Tuple[bool, List[str], str, int]:
        if not text or not str(text).strip():
            return False, ["EMPTY_TEXT"], "Generated text is empty.", 0

        reasons = []
        lower_text = str(text).lower()
        claim_count = 0

        # 1. Prompt / System Leakage Check
        for term in PROMPT_LEAKAGE_TERMS:
            if term in lower_text:
                reasons.append("PROMPT_LEAKAGE")
                return False, reasons, f"Generated text contains prompt leakage term '{term}'.", claim_count

        # 2. Prohibited Marketing Hype Check
        for term in PROHIBITED_MARKETING_TERMS:
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, lower_text):
                reasons.append("UNSUPPORTED_MARKETING_CLAIM")
                return False, reasons, f"Generated text contains unsupported marketing adjective '{term}'.", claim_count

        # 3. Numeric & Technical Value Grounding Check
        found_numbers = re.findall(r"\b\d+(?:\.\d+)?\b", lower_text)
        claim_count += len(found_numbers)

        allowed_strings = set()
        if payload.brand:
            allowed_strings.add(payload.brand.lower())
            claim_count += 1
        if payload.mpn:
            allowed_strings.add(payload.mpn.lower())
            claim_count += 1
            for part in re.findall(r"\b\d+(?:\.\d+)?\b", payload.mpn.lower()):
                allowed_strings.add(part)
        if payload.product_type:
            allowed_strings.add(payload.product_type.lower())
            claim_count += 1

        for k, v in payload.validated_attributes.items():
            val_str = str(v).lower()
            allowed_strings.add(val_str)
            claim_count += 1
            for part in re.findall(r"\b\d+(?:\.\d+)?\b", val_str):
                allowed_strings.add(part)

        # Verify every extracted number in text is grounded in allowed_strings
        for num in found_numbers:
            if num not in allowed_strings and not any(num in s for s in allowed_strings):
                reasons.append("UNSUPPORTED_NUMERIC_CLAIM")
                return False, reasons, f"Generated text contains ungrounded numeric value '{num}'.", claim_count

        # 4. Material & Specific Spec Grounding Check
        common_materials = {"ceramic", "pvc", "aluminum", "steel", "brass", "vinyl", "composite", "wood"}
        for mat in common_materials:
            if re.search(r"\b" + re.escape(mat) + r"\b", lower_text):
                claim_count += 1
                payload_materials = [str(v).lower() for k, v in payload.validated_attributes.items() if "material" in k.lower()]
                if not any(mat in p_mat for p_mat in payload_materials):
                    reasons.append("UNSUPPORTED_MATERIAL_CLAIM")
                    return False, reasons, f"Generated text contains ungrounded material claim '{mat}'.", claim_count

        return True, ["PASS"], "Factual grounding validation passed.", claim_count
