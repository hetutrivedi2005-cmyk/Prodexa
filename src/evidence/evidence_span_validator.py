import re
from typing import Dict, Any, Tuple, Optional


class EvidenceSpanValidator:
    """
    Component 1 (Phase 9.1): Evidence Span Validator.
    Locates exact evidence text match indices and validates explicit text grounding
    or deterministic Phase 7 UOM transformations. Rejects unstated specs and semantic guesses.
    """

    def validate_span(
        self,
        attribute_name: str,
        value: Any,
        evidence_text: str,
        section: str = "SPECIFICATIONS",
        page_number: Optional[int] = None
    ) -> Dict[str, Any]:
        if not evidence_text or not str(evidence_text).strip():
            return {
                "grounded": False,
                "reason": "missing_evidence_text",
                "matched_text": "",
                "match_start": -1,
                "match_end": -1,
                "evidence_location": section,
                "page_number": page_number,
                "section": section
            }

        if value is None or str(value).strip().lower() in ["", "none", "null", "nan"]:
            return {
                "grounded": False,
                "reason": "null_value",
                "matched_text": "",
                "match_start": -1,
                "match_end": -1,
                "evidence_location": section,
                "page_number": page_number,
                "section": section
            }

        val_str = str(value).strip()
        text = str(evidence_text)
        val_lower = val_str.lower()
        text_lower = text.lower()

        # 1. Direct exact substring match
        start_idx = text_lower.find(val_lower)
        if start_idx != -1:
            end_idx = start_idx + len(val_str)
            matched = text[start_idx:end_idx]
            return {
                "grounded": True,
                "reason": "explicit_exact_span_match",
                "matched_text": matched,
                "match_start": start_idx,
                "match_end": end_idx,
                "evidence_location": section,
                "page_number": page_number,
                "section": section
            }

        # 2. Case / Punctuation-insensitive match
        clean_val = re.sub(r"[^\w]", "", val_lower)
        clean_text = re.sub(r"[^\w]", "", text_lower)
        start_idx = clean_text.find(clean_val)
        if start_idx != -1:
            end_idx = start_idx + len(clean_val)
            return {
                "grounded": True,
                "reason": "explicit_normalized_span_match",
                "matched_text": clean_val,
                "match_start": start_idx,
                "match_end": end_idx,
                "evidence_location": section,
                "page_number": page_number,
                "section": section
            }

        # 3. Deterministic Phase 7 UOM Transformation (e.g., '0.5 in' -> '1/2 in')
        if attribute_name in ["dimensions", "belt_dimensions", "length", "width_profile", "diameter", "arbor_size", "drive_size"]:
            nums = re.findall(r"\d+(?:\.\d+)?|\d+\/\d+", val_str)
            if nums and all(n in text for n in nums):
                m_start = text.find(nums[0])
                m_end = m_start + len(nums[0]) if m_start != -1 else 0
                return {
                    "grounded": True,
                    "reason": "deterministic_uom_span_match",
                    "matched_text": nums[0],
                    "match_start": m_start,
                    "match_end": m_end,
                    "evidence_location": section,
                    "page_number": page_number,
                    "section": section
                }

        # 4. Enum Number Match (e.g. '120 grit' -> 'P120', '60W' -> '60 w')
        if attribute_name in ["grit", "wattage", "voltage", "color_temperature", "quantity"]:
            num_match = re.search(r"\d+", val_str)
            if num_match:
                num_str = num_match.group(0)
                n_idx = text.find(num_str)
                if n_idx != -1:
                    return {
                        "grounded": True,
                        "reason": "deterministic_numeric_enum_span_match",
                        "matched_text": num_str,
                        "match_start": n_idx,
                        "match_end": n_idx + len(num_str),
                        "evidence_location": section,
                        "page_number": page_number,
                        "section": section
                    }

        # Semantic guess or unsupported value
        return {
            "grounded": False,
            "reason": f"unsupported_semantic_guess_val_{val_str}",
            "matched_text": "",
            "match_start": -1,
            "match_end": -1,
            "evidence_location": section,
            "page_number": page_number,
            "section": section
        }
