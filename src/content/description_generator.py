import re
from typing import Dict, Any, Tuple
from src.content.validated_attribute_gate import VerifiedAttributePayload
from src.content.content_rules import ContentRuleEngine

PROHIBITED_MARKETING_TERMS = {
    "premium", "best", "high-performance", "industry-leading", "durable",
    "long-lasting", "professional-grade", "guaranteed", "superior",
    "heavy-duty", "top-rated", "unbeatable", "ultimate", "state-of-the-art"
}


class DescriptionGenerator:
    """
    Component 3 (Phase 13): Description Generator Engine.
    Generates evidence-grounded titles, short descriptions, and long descriptions
    from VerifiedAttributePayloads while filtering out unauthorized marketing hype.
    """

    def __init__(self):
        self.rule_engine = ContentRuleEngine()

    def generate_product_title(self, payload: VerifiedAttributePayload) -> str:
        title = self.rule_engine.build_title_template(payload)
        return self._sanitize_text(title)

    def generate_short_description(self, payload: VerifiedAttributePayload) -> str:
        short_desc = self.rule_engine.build_short_description_template(payload)
        return self._sanitize_text(short_desc)

    def generate_long_description(self, payload: VerifiedAttributePayload) -> str:
        long_desc = self.rule_engine.build_long_description_template(payload)
        return self._sanitize_text(long_desc)

    def generate_all_descriptions(self, payload: VerifiedAttributePayload) -> Dict[str, str]:
        return {
            "product_title": self.generate_product_title(payload),
            "short_description": self.generate_short_description(payload),
            "long_description": self.generate_long_description(payload)
        }

    def _sanitize_text(self, text: str) -> str:
        words = text.split()
        sanitized = []
        for w in words:
            clean_w = re.sub(r"[^\w-]", "", w).lower()
            if clean_w in PROHIBITED_MARKETING_TERMS:
                continue
            sanitized.append(w)
        return " ".join(sanitized).strip()
