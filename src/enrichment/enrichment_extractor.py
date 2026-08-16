import re
import json
from typing import Dict, List, Any, Optional


class EvidenceEnrichmentExtractor:
    """
    Component 9 (Phase 8.1 Enhanced): Evidence-Based Attribute Extraction Engine.
    Extracts missing category attributes strictly from retrieved evidence text.
    Enforces Anti-Hallucination Contract: returns value = None if evidence does not explicitly support it.
    """

    def extract_attributes_from_evidence(
        self,
        mpn: str,
        category_id: str,
        missing_attributes: List[str],
        attribute_evidence_map: Dict[str, List[dict]]
    ) -> Dict[str, Optional[dict]]:
        extracted_results: Dict[str, Optional[dict]] = {}

        for attr in missing_attributes:
            chunks = attribute_evidence_map.get(attr, [])
            if not chunks:
                extracted_results[attr] = None
                continue

            extracted_candidate = None
            for chunk in chunks:
                text = chunk.get("text", "")
                val = self._extract_value_from_text(attr, text)

                if val is not None:
                    extracted_candidate = {
                        "attribute_name": attr,
                        "value": str(val),
                        "normalized_value": str(val),
                        "source_id": chunk.get("source_id"),
                        "source_url": chunk.get("source_url"),
                        "source_type": chunk.get("source_type"),
                        "evidence_text": text,
                        "page": chunk.get("page", 1),
                        "attribute_confidence": 0.95 if chunk.get("source_type") in ["manufacturer_product_page", "manufacturer_pdf"] else 0.75,
                        "extraction_method": f"manufacturer_evidence_{chunk.get('source_type', 'rule')}"
                    }
                    break

            extracted_results[attr] = extracted_candidate

        return extracted_results

    def _extract_value_from_text(self, attribute_name: str, text: str) -> Optional[Any]:
        text_lower = text.lower()

        # 1. Material / Abrasive Type
        if attribute_name in ["material", "abrasive_type"]:
            if "pvc" in text_lower:
                return "PVC"
            elif "composite decking" in text_lower or "composite" in text_lower:
                return "Composite"
            elif "aluminum oxide" in text_lower:
                return "Aluminum Oxide"
            elif "ceramic" in text_lower or "cubitron" in text_lower:
                return "Ceramic"
            elif "zirconia" in text_lower:
                return "Zirconia Alumina"
            elif "silicon carbide" in text_lower:
                return "Silicon Carbide"
            elif "high speed steel" in text_lower or "hss" in text_lower:
                return "High Speed Steel"
            elif "aluminum" in text_lower:
                return "Aluminum"
            elif "vinyl" in text_lower:
                return "Vinyl"

        # 2. Dimensions / Belt Dimensions
        elif attribute_name in ["dimensions", "belt_dimensions"]:
            m = re.search(r"(\d+(?:\.\d+)?(?:\/\d+)?(?:\s+in|\"|\s+mm)?\s*x\s*\d+(?:\.\d+)?(?:\/\d+)?(?:\s+in|\"|\s+mm)?)", text, re.IGNORECASE)
            if m:
                return m.group(1).strip()

        # 3. Board / Rail Length
        elif attribute_name == "length":
            m = re.search(r"\b(\d+\s*ft|\d+\')\b", text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
            elif "12 ft" in text_lower:
                return "12 ft"
            elif "16 ft" in text_lower:
                return "16 ft"
            elif "8 ft" in text_lower:
                return "8 ft"
            elif "6 ft" in text_lower:
                return "6 ft"

        # 4. Width / Profile Size
        elif attribute_name == "width_profile":
            m = re.search(r"\b(1x6|4x4|6x6|1x8|1x12)\b", text, re.IGNORECASE)
            if m:
                return m.group(1).strip()

        # 5. Color / Tone / Finish
        elif attribute_name in ["color", "color_finish", "color_tone"]:
            if "slate gray" in text_lower or "slate grey" in text_lower:
                return "Slate Gray"
            elif "stainless steel" in text_lower:
                return "Stainless Steel"
            elif "brushed nickel" in text_lower:
                return "Brushed Nickel"
            elif "coastline" in text_lower:
                return "Coastline"
            elif "english walnut" in text_lower:
                return "English Walnut"
            elif "white" in text_lower:
                return "White"
            elif "black" in text_lower:
                return "Black"
            elif "charcoal" in text_lower:
                return "Charcoal"

        # 6. Edge Profile
        elif attribute_name == "edge_profile":
            if "grooved" in text_lower:
                return "Grooved"
            elif "square edge" in text_lower or "sq edge" in text_lower:
                return "Square Edge"
            elif "fascia" in text_lower:
                return "Fascia"

        # 7. Wattage
        elif attribute_name == "wattage":
            m = re.search(r"\b(\d{1,3}\s*W|\d{1,3}W)\b", text, re.IGNORECASE)
            if m:
                return m.group(1).strip().upper()

        # 8. Color Temperature
        elif attribute_name == "color_temperature":
            m = re.search(r"\b(2700K|3000K|4000K|5000K|27K|30K|40K|50K)\b", text, re.IGNORECASE)
            if m:
                val = m.group(1).upper()
                return "2700K" if "27" in val else "3000K" if "30" in val else "4000K" if "40" in val else "5000K"

        # 9. Power Type / Power Source
        elif attribute_name == "power_type":
            if "electric" in text_lower:
                return "Electric"
            elif "gas" in text_lower:
                return "Gas"

        # 10. Display Status / Condition
        elif attribute_name == "display_status":
            if "display only" in text_lower:
                return "Display Only"
            elif "new" in text_lower:
                return "New"

        # 11. Drive Size / Arbor Hole Size
        elif attribute_name in ["drive_size", "arbor_size"]:
            m = re.search(r"\b(1/4 in|3/8 in|1/2 in|7/8 in|5/8 in|20mm|1 in)\b", text, re.IGNORECASE)
            if m:
                return m.group(1).strip()

        # 12. Grit Rating
        elif attribute_name == "grit":
            m = re.search(r"\b(P\d{2,4}|\d{2,4}\s*grit)\b", text, re.IGNORECASE)
            if m:
                return m.group(1).strip()

        # 13. Pack Quantity
        elif attribute_name in ["pack_quantity", "quantity"]:
            m = re.search(r"\b(\d+)\s*(?:pack|pcs|per box|belts|discs|pack quantity)\b", text, re.IGNORECASE)
            if m:
                return int(m.group(1))

        return None
