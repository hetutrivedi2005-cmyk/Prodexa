from typing import List, Dict, Any
from src.content.validated_attribute_gate import VerifiedAttributePayload

KEY_SPEC_ATTRIBUTES = ["material", "grit", "dimensions", "belt_dimensions", "voltage", "wattage", "color_temperature", "color_finish", "pack_quantity", "arbor_size", "diameter", "drive_size"]


class ContentRuleEngine:
    """
    Component 2 (Phase 13): Content Rule Engine.
    Defines deterministic natural-language content templates for product titles,
    short descriptions, and long descriptions grounded in verified attributes.
    """

    def build_title_template(self, payload: VerifiedAttributePayload) -> str:
        parts: List[str] = []

        if payload.brand:
            parts.append(payload.brand)
        if payload.mpn:
            parts.append(payload.mpn)

        # Include key spec attributes
        spec_parts: List[str] = []
        for key in KEY_SPEC_ATTRIBUTES:
            if key in payload.validated_attributes:
                val = str(payload.validated_attributes[key]).strip()
                if val and val not in spec_parts:
                    spec_parts.append(val)

        if payload.product_type:
            parts.append(payload.product_type)

        if spec_parts:
            parts.append("– " + ", ".join(spec_parts[:3]))

        return " ".join(parts).strip()

    def build_short_description_template(self, payload: VerifiedAttributePayload) -> str:
        ident_parts = []
        if payload.brand:
            ident_parts.append(payload.brand)
        if payload.mpn:
            ident_parts.append(payload.mpn)

        p_type = payload.product_type or "product"
        subject = f"The {' '.join(ident_parts)} {p_type}".strip()

        specs: List[str] = []
        for k, v in payload.validated_attributes.items():
            if k in KEY_SPEC_ATTRIBUTES:
                specs.append(f"{k.replace('_', ' ')} of {v}")

        if specs:
            spec_str = " with " + " and ".join(specs[:3])
        else:
            spec_str = ""

        return f"{subject} is a verified {p_type}{spec_str}.".strip()

    def build_long_description_template(self, payload: VerifiedAttributePayload) -> str:
        lines: List[str] = []

        # Header / Overview
        lines.append("[Product Overview]")
        ident = []
        if payload.brand:
            ident.append(f"Brand: {payload.brand}")
        if payload.mpn:
            ident.append(f"MPN: {payload.mpn}")
        if payload.product_type:
            ident.append(f"Product Type: {payload.product_type}")

        if ident:
            lines.append(" | ".join(ident))

        lines.append("")
        lines.append("[Verified Specifications]")
        if payload.validated_attributes:
            for k, v in payload.validated_attributes.items():
                if k not in ["brand", "mpn", "product_type"]:
                    lines.append(f"• {k.replace('_', ' ').title()}: {v}")
        else:
            lines.append("• No additional attribute specifications verified.")

        lines.append("")
        lines.append("[Product Details]")
        lines.append("This product listing contains specifications verified by the Prodexa validation and evidence pipeline.")

        return "\n".join(lines).strip()
