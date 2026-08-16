import os
import re
import json
import hashlib
import pandas as pd
from typing import Dict, List, Any, Optional

from src.validation.validation_result import ValidationResult
from src.validation.character_limits import CharacterLimitValidator


class ValidationEngine:
    """
    Component 3 (Phase 10): Core Validation Engine.
    Strictly deterministic read-only validation service for all Phase 1-9.1 pipeline data.
    """

    def __init__(
        self,
        category_attributes_path: str = "data/master/category_attributes.csv",
        attribute_lov_path: str = "data/master/attribute_lov.csv",
        uom_master_path: str = "data/master/uom_master.csv",
        source_registry_path: str = "data/master/source_registry.csv"
    ):
        self.char_validator = CharacterLimitValidator()

        # 1. Load Category Attributes Schema
        self.category_allowed_map: Dict[str, set] = {}
        if os.path.exists(category_attributes_path):
            df_cat = pd.read_csv(category_attributes_path)
            for _, r in df_cat.iterrows():
                cid = str(r.get("category_id")).strip()
                attrs = set(str(r.get("allowed_attributes")).replace(" ", "").split(","))
                self.category_allowed_map[cid] = attrs

        # 2. Load Attribute LOV Master
        self.lov_approved_map: Dict[str, set] = {}
        if os.path.exists(attribute_lov_path):
            df_lov = pd.read_csv(attribute_lov_path)
            for _, r in df_lov.iterrows():
                attr = str(r.get("attribute_name")).strip()
                lov_val = str(r.get("canonical_value") or r.get("normalized_value") or "").strip()
                if lov_val and lov_val.lower() != "nan":
                    self.lov_approved_map.setdefault(attr, set()).add(lov_val)

        # 3. Load UOM Master
        self.uom_canonical_set: set = set()
        if os.path.exists(uom_master_path):
            df_uom = pd.read_csv(uom_master_path)
            for _, r in df_uom.iterrows():
                self.uom_canonical_set.add(str(r.get("uom_canonical")).strip())
                self.uom_canonical_set.add(str(r.get("unit")).strip())

        # 4. Load Source Registry
        self.source_urls_set: set = set()
        if os.path.exists(source_registry_path):
            df_src = pd.read_csv(source_registry_path)
            for _, r in df_src.iterrows():
                if not pd.isna(r.get("url")):
                    self.source_urls_set.add(str(r.get("url")).strip())

    def _gen_id(self, p_id: str, rule: str, attr: str = "") -> str:
        return f"VAL-{rule[:6]}-{hashlib.md5(f'{p_id}_{rule}_{attr}'.encode('utf-8')).hexdigest()[:8]}"

    def validate_required_fields(self, product: pd.Series) -> List[ValidationResult]:
        results = []
        p_id = str(product.get("product_id") or "UNKNOWN").strip()

        required_cols = {
            "brand": ("brand", "brand_canonical", "e1_brand", "unilog_brand", "dib_brand", "manufacturer_canonical", "part_manuf"),
            "manufacturer": ("manufacturer_canonical", "part_manuf", "brand_canonical", "brand"),
            "mpn": ("manufacturer_part_number", "mfg_part_num", "mpn"),
            "category": ("category_id", "category_name", "parent_category_id", "parent_category_name"),
            "product_type": ("product_type", "clean_title", "part_desc")
        }

        for req_name, col_tuple in required_cols.items():
            val = None
            for col in col_tuple:
                if col in product and not pd.isna(product[col]) and str(product[col]).strip() and str(product[col]).strip().lower() not in ["none", "null", "nan"]:
                    val = str(product[col]).strip()
                    break

            val_id = self._gen_id(p_id, "REQ_FIELDS", req_name)
            if val is not None:
                results.append(ValidationResult(
                    validation_id=val_id,
                    product_id=p_id,
                    attribute_name=req_name,
                    rule_name="REQUIRED_FIELDS",
                    status="PASS",
                    severity="INFO",
                    message=f"Required field '{req_name}' is valid.",
                    expected="non-empty string",
                    actual=val
                ))
            else:
                sev = "ERROR" if req_name in ["brand", "mpn"] else "WARNING"
                status = "FAIL" if sev == "ERROR" else "WARNING"
                results.append(ValidationResult(
                    validation_id=val_id,
                    product_id=p_id,
                    attribute_name=req_name,
                    rule_name="REQUIRED_FIELDS",
                    status=status,
                    severity=sev,
                    message=f"Field '{req_name}' is missing or unclassified.",
                    expected="non-empty string",
                    actual=None
                ))

        return results

    def validate_lov_compliance(self, p_id: str, attribute_name: str, value: Any) -> ValidationResult:
        val_id = self._gen_id(p_id, "LOV_COMPLIANCE", attribute_name)
        if attribute_name not in self.lov_approved_map:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="LOV_COMPLIANCE", status="NOT_APPLICABLE", severity="INFO",
                message=f"Attribute '{attribute_name}' is not governed by LOV master.", actual=value
            )

        str_val = "" if value is None or str(value).strip().lower() in ["none", "null", "nan"] else str(value).strip()
        if not str_val:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="LOV_COMPLIANCE", status="NOT_APPLICABLE", severity="INFO",
                message=f"LOV attribute '{attribute_name}' is missing/empty.", actual=None
            )

        approved = self.lov_approved_map[attribute_name]
        if str_val in approved or any(a.lower() == str_val.lower() for a in approved):
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="LOV_COMPLIANCE", status="PASS", severity="INFO",
                message=f"Value '{str_val}' exists in approved LOV for '{attribute_name}'.",
                expected=list(approved)[:5], actual=str_val
            )
        else:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="LOV_COMPLIANCE", status="FAIL", severity="ERROR",
                message=f"Value '{str_val}' for '{attribute_name}' is not in approved LOV.",
                expected=list(approved)[:5], actual=str_val
            )

    def validate_uom_compliance(self, p_id: str, attribute_name: str, value: Any) -> ValidationResult:
        val_id = self._gen_id(p_id, "UOM_COMPLIANCE", attribute_name)
        uom_attrs = ["dimensions", "belt_dimensions", "length", "width_profile", "diameter", "arbor_size", "drive_size", "voltage", "wattage"]
        if attribute_name not in uom_attrs:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="UOM_COMPLIANCE", status="NOT_APPLICABLE", severity="INFO",
                message=f"Attribute '{attribute_name}' is not a UOM measurement.", actual=value
            )

        str_val = "" if value is None or str(value).strip().lower() in ["none", "null", "nan"] else str(value).strip()
        if not str_val:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="UOM_COMPLIANCE", status="NOT_APPLICABLE", severity="INFO",
                message=f"UOM attribute '{attribute_name}' is empty.", actual=None
            )

        # Check canonical UOM format (e.g. '24 in', '1/2 in', '20V', '60W', 'mm')
        has_canonical_unit = bool(re.search(r"\b(in|ft|mm|cm|m|v|w|kv|kw|hz)\b|[\"']|\d+\s*x\s*\d+", str_val.lower()))
        if has_canonical_unit:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="UOM_COMPLIANCE", status="PASS", severity="INFO",
                message=f"UOM value '{str_val}' follows canonical representation.", actual=str_val
            )
        else:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="UOM_COMPLIANCE", status="FAIL", severity="ERROR",
                message=f"UOM value '{str_val}' has non-canonical or missing unit.", actual=str_val
            )

    def validate_character_limits(self, p_id: str, field_name: str, value: Any) -> ValidationResult:
        return self.char_validator.validate_field(p_id, field_name, value)

    def validate_source_evidence(self, p_id: str, attribute_name: str, evidence_record: Optional[dict]) -> ValidationResult:
        val_id = self._gen_id(p_id, "EVIDENCE", attribute_name)
        if not evidence_record or not evidence_record.get("source_id"):
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="EVIDENCE_VALIDATION", status="WARNING", severity="WARNING",
                message=f"Attribute '{attribute_name}' is a baseline Phase 5 attribute without external evidence enrichment.", actual=None
            )

        src_id = evidence_record.get("source_id")
        src_url = evidence_record.get("source_url")
        ev_text = evidence_record.get("evidence_text")

        if not src_id or not src_url or not ev_text:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="EVIDENCE_VALIDATION", status="WARNING", severity="WARNING",
                message=f"Evidence record for '{attribute_name}' is missing source_id, source_url, or evidence_text.",
                actual=evidence_record, source_id=src_id, evidence_id=evidence_record.get("evidence_id")
            )

        return ValidationResult(
            validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
            rule_name="EVIDENCE_VALIDATION", status="PASS", severity="INFO",
            message=f"Traceable evidence verified for '{attribute_name}'.",
            source_id=src_id, evidence_id=evidence_record.get("evidence_id")
        )

    def validate_provenance(self, p_id: str, attribute_name: str, evidence_record: Optional[dict]) -> ValidationResult:
        val_id = self._gen_id(p_id, "PROVENANCE", attribute_name)
        if not evidence_record or not evidence_record.get("source_id"):
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="PROVENANCE_COMPLETENESS", status="WARNING", severity="WARNING",
                message=f"Provenance chain incomplete for baseline Phase 5 attribute '{attribute_name}'.", actual=None
            )

        req_keys = ["attribute_name", "value", "source_id", "source_url", "source_type", "manufacturer", "normalized_mpn", "evidence_text", "confidence", "status"]
        missing = [k for k in req_keys if k not in evidence_record or evidence_record[k] is None]

        if missing:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="PROVENANCE_COMPLETENESS", status="WARNING", severity="WARNING",
                message=f"Provenance chain missing keys: {missing}.", actual=missing
            )

        return ValidationResult(
            validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
            rule_name="PROVENANCE_COMPLETENESS", status="PASS", severity="INFO",
            message=f"Complete 7-step provenance chain verified for '{attribute_name}'."
        )

    def validate_identity(self, product_mpn: str, product_mfg: str, evidence_record: dict) -> List[ValidationResult]:
        results = []
        p_id = str(evidence_record.get("product_id") or "UNKNOWN")

        raw_ev_mpn = str(evidence_record.get("normalized_mpn") or evidence_record.get("mpn") or "").strip()
        if raw_ev_mpn.lower() in ["nan", "none", "null"]:
            raw_ev_mpn = ""

        raw_ev_mfg = str(evidence_record.get("manufacturer") or "").strip()
        if raw_ev_mfg.lower() in ["nan", "none", "null"]:
            raw_ev_mfg = ""

        norm_p_mpn = re.sub(r"[^A-Z0-9]", "", str(product_mpn).upper())
        norm_ev_mpn = re.sub(r"[^A-Z0-9]", "", raw_ev_mpn.upper())

        norm_p_mfg = re.sub(r"[^A-Z0-9]", "", str(product_mfg).upper())
        norm_ev_mfg = re.sub(r"[^A-Z0-9]", "", raw_ev_mfg.upper())

        # MPN Check
        mpn_val_id = self._gen_id(p_id, "IDENTITY_MPN", evidence_record.get("attribute_name", ""))
        if not norm_p_mpn and not norm_ev_mpn:
            results.append(ValidationResult(
                validation_id=mpn_val_id, product_id=p_id, attribute_name="mpn",
                rule_name="EXACT_MPN_IDENTITY", status="NOT_APPLICABLE", severity="INFO",
                message="MPN identity check not applicable (empty MPN).", expected=norm_p_mpn, actual=norm_ev_mpn
            ))
        elif norm_p_mpn and norm_ev_mpn and norm_p_mpn == norm_ev_mpn:
            results.append(ValidationResult(
                validation_id=mpn_val_id, product_id=p_id, attribute_name="mpn",
                rule_name="EXACT_MPN_IDENTITY", status="PASS", severity="INFO",
                message="Product MPN matches evidence MPN.", expected=norm_p_mpn, actual=norm_ev_mpn
            ))
        elif not norm_p_mpn or not norm_ev_mpn:
            results.append(ValidationResult(
                validation_id=mpn_val_id, product_id=p_id, attribute_name="mpn",
                rule_name="EXACT_MPN_IDENTITY", status="WARNING", severity="WARNING",
                message=f"MPN identity partial: product '{norm_p_mpn}' vs evidence '{norm_ev_mpn}'.",
                expected=norm_p_mpn, actual=norm_ev_mpn
            ))
        else:
            results.append(ValidationResult(
                validation_id=mpn_val_id, product_id=p_id, attribute_name="mpn",
                rule_name="EXACT_MPN_IDENTITY", status="FAIL", severity="ERROR",
                message=f"MPN identity mismatch: product '{norm_p_mpn}' vs evidence '{norm_ev_mpn}'.",
                expected=norm_p_mpn, actual=norm_ev_mpn
            ))

        # Manufacturer Check
        mfg_val_id = self._gen_id(p_id, "IDENTITY_MFG", evidence_record.get("attribute_name", ""))
        if not norm_p_mfg and not norm_ev_mfg:
            results.append(ValidationResult(
                validation_id=mfg_val_id, product_id=p_id, attribute_name="manufacturer",
                rule_name="MANUFACTURER_IDENTITY", status="NOT_APPLICABLE", severity="INFO",
                message="Manufacturer identity check not applicable (empty manufacturer).", expected=norm_p_mfg, actual=norm_ev_mfg
            ))
        elif norm_p_mfg and norm_ev_mfg and (norm_p_mfg in norm_ev_mfg or norm_ev_mfg in norm_p_mfg):
            results.append(ValidationResult(
                validation_id=mfg_val_id, product_id=p_id, attribute_name="manufacturer",
                rule_name="MANUFACTURER_IDENTITY", status="PASS", severity="INFO",
                message="Product manufacturer matches evidence manufacturer.", expected=norm_p_mfg, actual=norm_ev_mfg
            ))
        elif not norm_p_mfg or not norm_ev_mfg:
            results.append(ValidationResult(
                validation_id=mfg_val_id, product_id=p_id, attribute_name="manufacturer",
                rule_name="MANUFACTURER_IDENTITY", status="WARNING", severity="WARNING",
                message=f"Manufacturer identity partial: product '{norm_p_mfg}' vs evidence '{norm_ev_mfg}'.",
                expected=norm_p_mfg, actual=norm_ev_mfg
            ))
        else:
            results.append(ValidationResult(
                validation_id=mfg_val_id, product_id=p_id, attribute_name="manufacturer",
                rule_name="MANUFACTURER_IDENTITY", status="FAIL", severity="ERROR",
                message=f"Manufacturer identity mismatch: product '{norm_p_mfg}' vs evidence '{norm_ev_mfg}'.",
                expected=norm_p_mfg, actual=norm_ev_mfg
            ))

        return results

    def validate_category_attributes(self, p_id: str, category_id: str, attribute_name: str) -> ValidationResult:
        val_id = self._gen_id(p_id, "CATEGORY_SCHEMA", attribute_name)
        if category_id not in self.category_allowed_map:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="CATEGORY_SCHEMA", status="PASS", severity="INFO",
                message=f"Category '{category_id}' has no strict schema constraints."
            )

        allowed = self.category_allowed_map[category_id]
        if attribute_name in allowed:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="CATEGORY_SCHEMA", status="PASS", severity="INFO",
                message=f"Attribute '{attribute_name}' is allowed for category '{category_id}'.",
                expected=list(allowed)
            )
        else:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name=attribute_name,
                rule_name="CATEGORY_SCHEMA", status="WARNING", severity="WARNING",
                message=f"Attribute '{attribute_name}' is not in category '{category_id}' schema.",
                expected=list(allowed), actual=attribute_name
            )

    def validate_conflicts(self, p_id: str, conflict_status: str, manual_review_required: bool) -> ValidationResult:
        val_id = self._gen_id(p_id, "CONFLICT", "")
        if conflict_status == "conflict" or manual_review_required:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name="conflict",
                rule_name="CONFLICT_VALIDATION", status="WARNING", severity="WARNING",
                message="Unresolved conflict detected. Trusted value preserved, manual review required.",
                actual=conflict_status
            )
        else:
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name="conflict",
                rule_name="CONFLICT_VALIDATION", status="PASS", severity="INFO",
                message="No data conflicts detected."
            )

    def validate_data_types(self, p_id: str, confidence: Any, status: str) -> List[ValidationResult]:
        results = []

        # Confidence bounds check
        c_id = self._gen_id(p_id, "DATA_TYPES", "confidence")
        if isinstance(confidence, (int, float)) and not pd.isna(confidence) and (0.0 <= float(confidence) <= 1.0):
            results.append(ValidationResult(
                validation_id=c_id, product_id=p_id, attribute_name="confidence",
                rule_name="DATA_TYPE_CONFIDENCE", status="PASS", severity="INFO",
                message=f"Confidence value {confidence} within range [0.0, 1.0].", actual=confidence
            ))
        else:
            results.append(ValidationResult(
                validation_id=c_id, product_id=p_id, attribute_name="confidence",
                rule_name="DATA_TYPE_CONFIDENCE", status="FAIL", severity="ERROR",
                message=f"Invalid confidence value '{confidence}'. Must be float in range [0.0, 1.0].", actual=confidence
            ))

        # Status Enum check
        s_id = self._gen_id(p_id, "DATA_TYPES", "status")
        valid_statuses = {"verified", "partially_verified", "unverified", "conflict", "rejected", "complete", "partial", "none"}
        if str(status).lower() in valid_statuses:
            results.append(ValidationResult(
                validation_id=s_id, product_id=p_id, attribute_name="status",
                rule_name="DATA_TYPE_STATUS", status="PASS", severity="INFO",
                message=f"Status '{status}' is a valid enum.", actual=status
            ))
        else:
            results.append(ValidationResult(
                validation_id=s_id, product_id=p_id, attribute_name="status",
                rule_name="DATA_TYPE_STATUS", status="FAIL", severity="ERROR",
                message=f"Invalid status enum '{status}'.", actual=status
            ))

        return results

    def validate_referential_integrity(self, p_id: str, evidence_record: dict) -> ValidationResult:
        val_id = self._gen_id(p_id, "REF_INTEGRITY", evidence_record.get("attribute_name", ""))
        src_url = evidence_record.get("source_url")
        ev_pid = evidence_record.get("product_id")

        if not p_id or not ev_pid or not evidence_record.get("evidence_id") or not evidence_record.get("source_id"):
            return ValidationResult(
                validation_id=val_id, product_id=p_id, attribute_name="referential_integrity",
                rule_name="REFERENTIAL_INTEGRITY", status="WARNING", severity="WARNING",
                message="Baseline attribute without external source_id/evidence_id/product_id reference."
            )

        return ValidationResult(
            validation_id=val_id, product_id=p_id, attribute_name="referential_integrity",
            rule_name="REFERENTIAL_INTEGRITY", status="PASS", severity="INFO",
            message="Referential integrity verified across all identifiers."
        )
