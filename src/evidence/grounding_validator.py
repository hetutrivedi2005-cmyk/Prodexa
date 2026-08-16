import re
from typing import Tuple, Any


class GroundingValidator:
    """
    Component 4 (Phase 9): Evidence Grounding Validator.
    Strictly verifies that extracted attribute value is explicitly established by evidence text.
    Rejects semantic guessing, unstated specs, and ungrounded values.
    """

    def validate_grounding(self, attribute_name: str, extracted_value: Any, evidence_text: str) -> Tuple[bool, str]:
        if not evidence_text or not str(evidence_text).strip():
            return False, "evidence_text_missing"

        if extracted_value is None or str(extracted_value).strip().lower() in ["", "none", "null", "nan"]:
            return False, "extracted_value_null"

        val_str = str(extracted_value).strip()
        text_lower = evidence_text.lower()
        val_lower = val_str.lower()

        # Exact substring or numeric/unit match check
        clean_val = re.sub(r"[^\w\s\./-]", "", val_lower)
        clean_text = re.sub(r"[^\w\s\./-]", "", text_lower)

        # 1. Exact string match in text
        if val_lower in text_lower or clean_val in clean_text:
            return True, "exact_grounded_match"

        # 2. Measurement / Fraction equivalence (e.g. '1/2 in' vs '0.5 in' or '0.5" x 18"')
        if attribute_name in ["dimensions", "belt_dimensions", "length", "width_profile", "diameter", "arbor_size", "drive_size"]:
            # Check numbers match in evidence
            nums = re.findall(r"\d+(?:\.\d+)?|\d+\/\d+", val_str)
            if nums and all(n in evidence_text for n in nums):
                return True, "numeric_dimension_grounded"

        # 3. Code / Enum aliases in text (e.g. 'P120' vs '120 grit', '60W' vs '60 w')
        if attribute_name == "grit":
            num = re.search(r"\d+", val_str)
            if num and num.group(0) in text_lower:
                return True, "grit_number_grounded"

        if attribute_name == "wattage":
            num = re.search(r"\d+", val_str)
            if num and num.group(0) in text_lower:
                return True, "wattage_number_grounded"

        if attribute_name == "color_temperature":
            num = re.search(r"\d{4}", val_str)
            if num and num.group(0) in text_lower:
                return True, "color_temp_number_grounded"

        return False, f"value '{val_str}' not explicitly supported by evidence text"
