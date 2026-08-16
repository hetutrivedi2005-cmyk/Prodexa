import re
from typing import Dict, Any, Optional


class EvidenceValidator:
    """
    Component 3 (Phase 9): Evidence Validator Engine.
    Performs deterministic validation on evidence sources, identities, schemas, LOV/UOM compliance.
    """

    def __init__(self):
        # Known LOVs per attribute
        self.known_lovs = {
            "material": {"PVC", "Composite", "Aluminum Oxide", "Ceramic", "Zirconia Alumina", "Silicon Carbide", "High Speed Steel", "Aluminum", "Vinyl"},
            "color": {"Slate Gray", "White", "Black", "Charcoal", "Coastline", "English Walnut", "French White Oak", "Stainless Steel", "Brushed Nickel"},
            "color_finish": {"Slate Gray", "White", "Black", "Charcoal", "Stainless Steel", "Brushed Nickel", "Juniper"},
            "edge_profile": {"Grooved", "Square Edge", "Fascia"},
            "power_type": {"Electric", "Gas"},
            "display_status": {"Display Only", "New"}
        }

    def validate_evidence(
        self,
        attribute_name: str,
        value: Any,
        source_info: dict,
        category_id: str,
        allowed_attributes: set,
        evidence_text: str
    ) -> Dict[str, Any]:
        val_checks = {
            "source_exists": bool(source_info.get("source_id") or source_info.get("url")),
            "source_url_valid": bool(source_info.get("url") and ("http" in source_info.get("url") or "https" in source_info.get("url"))),
            "manufacturer_verified": bool(source_info.get("manufacturer_verified", True)),
            "mpn_verified": bool(source_info.get("mpn_verified", True)),
            "evidence_text_nonempty": bool(evidence_text and len(str(evidence_text).strip()) > 0),
            "attribute_allowed_for_category": attribute_name in allowed_attributes if allowed_attributes else True,
            "lov_valid": True,
            "uom_valid": True
        }

        # LOV Validation
        if attribute_name in self.known_lovs:
            str_val = str(value).strip()
            val_checks["lov_valid"] = str_val in self.known_lovs[attribute_name] or any(k.lower() == str_val.lower() for k in self.known_lovs[attribute_name])

        # UOM Validation
        if attribute_name in ["dimensions", "belt_dimensions", "length", "width_profile", "diameter", "arbor_size", "drive_size"]:
            str_val = str(value).strip()
            val_checks["uom_valid"] = any(u in str_val.lower() for u in ["in", "ft", "mm", "x", "\""])

        all_passed = all(val_checks.values())

        if not val_checks["source_exists"] or not val_checks["source_url_valid"] or not val_checks["evidence_text_nonempty"]:
            status = "unverified"
        elif not val_checks["mpn_verified"] or not val_checks["manufacturer_verified"]:
            status = "rejected"
        elif not all_passed:
            status = "partially_verified"
        else:
            status = "verified"

        return {
            "checks": val_checks,
            "all_passed": all_passed,
            "status": status,
            "lov_valid": val_checks["lov_valid"],
            "uom_valid": val_checks["uom_valid"],
            "mpn_verified": val_checks["mpn_verified"],
            "manufacturer_verified": val_checks["manufacturer_verified"]
        }
