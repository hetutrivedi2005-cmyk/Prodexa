import pandas as pd
from typing import List, Dict


class ErrorAnalyzer:
    """
    Component 11 (Phase 15): Error Analyzer.
    Groups evaluation mismatches by attribute and categories to produce ranked error tables.
    """

    def analyze_errors(self, comparison_records: List[dict]) -> pd.DataFrame:
        """
        Analyzes comparison records to identify top error categories.
        Filters for statuses of MISMATCH or MISSING.
        """
        errors = [r for r in comparison_records if r.get("comparison_status") in ["MISMATCH", "MISSING"]]
        if not errors:
            return pd.DataFrame(columns=["ATTRIBUTE", "MISMATCHES", "RATE"])

        total_evals = len(comparison_records)
        df_errors = pd.DataFrame(errors)

        # Count mismatches per attribute
        counts = df_errors["field_name"].value_counts().reset_index()
        counts.columns = ["ATTRIBUTE", "MISMATCHES"]

        # Calculate rate relative to total comparisons
        counts["RATE"] = (counts["MISMATCHES"] / total_evals * 100).round(2).astype(str) + "%"
        return counts
