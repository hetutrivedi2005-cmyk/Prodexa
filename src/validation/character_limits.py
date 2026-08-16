import hashlib
from typing import Dict, Any, List, Optional
from src.validation.validation_result import ValidationResult


DEFAULT_CHARACTER_LIMITS = {
    "invoice_description": 50,
    "product_description": 500,
    "short_description": 100,
    "display_name": 100,
    "title": 150,
    "brand": 50,
    "part_manuf": 50,
    "manufacturer_part_number": 50,
    "mfg_part_num": 50
}


class CharacterLimitValidator:
    """
    Component 2 (Phase 10): Character Limit Validator Engine.
    Validates configured field lengths against schema limits.
    Never truncates or rewrites data.
    """

    def __init__(self, limits: Optional[Dict[str, int]] = None):
        self.limits = limits or DEFAULT_CHARACTER_LIMITS

    def validate_field(self, product_id: str, field_name: str, value: Any) -> ValidationResult:
        max_len = self.limits.get(field_name, 500)
        str_val = "" if value is None or str(value).strip().lower() in ["none", "null", "nan"] else str(value).strip()
        actual_len = len(str_val)

        val_id = f"VAL-CHAR-{hashlib.md5(f'{product_id}_{field_name}'.encode('utf-8')).hexdigest()[:8]}"

        if actual_len <= max_len:
            return ValidationResult(
                validation_id=val_id,
                product_id=product_id,
                attribute_name=field_name,
                rule_name="CHARACTER_LIMIT",
                status="PASS",
                severity="INFO",
                message=f"Field '{field_name}' length ({actual_len}) within max limit ({max_len}).",
                expected=f"<= {max_len}",
                actual=actual_len
            )
        else:
            return ValidationResult(
                validation_id=val_id,
                product_id=product_id,
                attribute_name=field_name,
                rule_name="CHARACTER_LIMIT",
                status="FAIL",
                severity="ERROR",
                message=f"Field '{field_name}' length ({actual_len}) exceeded maximum allowed limit ({max_len}). Overflow: {actual_len - max_len} chars.",
                expected=f"<= {max_len}",
                actual=actual_len
            )
