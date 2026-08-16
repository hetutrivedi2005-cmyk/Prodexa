from typing import List, Dict, Tuple
from src.validation.validation_result import ValidationResult


class ProductQualityGate:
    """
    Component 4 (Phase 10): Product Quality Gate Evaluator.
    Determines final product-level status (PASS, PASS_WITH_WARNINGS, FAIL) based on validation results.
    Never hides individual failures behind product-level summary status.
    """

    def evaluate_quality_gate(self, results: List[ValidationResult]) -> Tuple[str, int, int]:
        errors = [r for r in results if r.status == "FAIL" or r.severity == "ERROR"]
        warnings = [r for r in results if r.status == "WARNING" or r.severity == "WARNING"]

        error_count = len(errors)
        warning_count = len(warnings)

        if error_count > 0:
            status = "FAIL"
        elif warning_count > 0:
            status = "PASS_WITH_WARNINGS"
        else:
            status = "PASS"

        return status, error_count, warning_count
