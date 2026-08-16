from typing import Dict, Any, List, Tuple

DEFAULT_DESCRIPTION_LIMITS = {
    "product_title": 150,
    "short_description": 500,
    "long_description": 2000
}


class DescriptionValidator:
    """
    Component 5 (Phase 13): Quality & Character Limit Validator.
    Validates field character limits and formatting quality constraints.
    Never silently truncates content.
    """

    def __init__(self, limits: Dict[str, int] = None):
        self.limits = limits or DEFAULT_DESCRIPTION_LIMITS

    def validate_description(self, field_name: str, text: str) -> Tuple[bool, List[str], str]:
        if not text or not str(text).strip():
            return False, ["EMPTY_DESCRIPTION"], f"Field '{field_name}' description is empty."

        clean_text = str(text).strip()
        actual_len = len(clean_text)
        max_len = self.limits.get(field_name, 2000)

        # 1. Character Limit Check
        if actual_len > max_len:
            return False, ["CHARACTER_LIMIT_EXCEEDED"], f"Field '{field_name}' length ({actual_len}) exceeded maximum allowed limit ({max_len})."

        # 2. Quality Formatting Checks
        if "  " in clean_text and "\n" not in clean_text:
            pass  # Allow newline formatted text

        # Check for duplicated sentences
        sentences = [s.strip().lower() for s in clean_text.replace("\n", ". ").split(".") if s.strip()]
        if len(sentences) != len(set(sentences)) and len(sentences) > 1:
            return False, ["DUPLICATE_TEXT"], f"Field '{field_name}' contains duplicate sentence phrasing."

        return True, ["PASS"], f"Field '{field_name}' quality and character limit validation passed."
