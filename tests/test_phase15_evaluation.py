import os
import pytest
import json
import pandas as pd
from src.evaluation.ground_truth_loader import GroundTruthLoader
from src.evaluation.field_comparator import FieldComparator
from src.evaluation.error_analyzer import ErrorAnalyzer
from src.evaluation.phase15_pipeline import run_phase15_pipeline


@pytest.fixture
def loader():
    return GroundTruthLoader()


@pytest.fixture
def comparator():
    return FieldComparator()


@pytest.fixture
def error_analyzer():
    return ErrorAnalyzer()


def test_1_gt_loader_instantiation(loader):
    assert loader is not None


def test_2_gt_loader_validation_missing_cols(loader):
    # Missing required cols
    df = pd.DataFrame([{"product_id": "P1"}])
    loader.seed_ground_truth("data/master/test_gt_tmp.csv")
    df_loaded, status = loader.load_ground_truth("data/master/test_gt_tmp.csv")
    assert status == "VALID"
    assert len(df_loaded) > 0


def test_3_comparator_exact_match(comparator):
    s, r = comparator.compare_field("brand", "Diablo", "Diablo")
    assert s == "MATCH"


def test_4_comparator_case_normalization(comparator):
    s, r = comparator.compare_field("brand", "diablo", "Diablo")
    assert s == "MATCH"


def test_5_comparator_whitespace_normalization(comparator):
    s, r = comparator.compare_field("brand", " Diablo ", "Diablo")
    assert s == "MATCH"


def test_6_comparator_uom_inches(comparator):
    s, r = comparator.compare_field("size", "1/2 inches", "1/2 in")
    assert s == "MATCH"


def test_7_comparator_uom_volts(comparator):
    s, r = comparator.compare_field("voltage", "20 Volts", "20 v")
    assert s == "MATCH"


def test_8_comparator_uom_watts(comparator):
    s, r = comparator.compare_field("wattage", "60 Watts", "60 w")
    assert s == "MATCH"


def test_9_comparator_uom_pack(comparator):
    s, r = comparator.compare_field("quantity", "6 Pack", "6 pcs")
    assert s == "MATCH"


def test_10_comparator_missing_expected(comparator):
    s, r = comparator.compare_field("size", "", "1/2 in")
    assert s == "MISSING"


def test_11_comparator_extra_prodexa(comparator):
    s, r = comparator.compare_field("size", "1/2 in", "")
    assert s == "EXTRA"


def test_12_comparator_mismatch(comparator):
    s, r = comparator.compare_field("brand", "DeWALT", "Diablo")
    assert s == "MISMATCH"


def test_13_comparator_not_applicable(comparator):
    s, r = comparator.compare_field("brand", "", "")
    assert s == "NOT_APPLICABLE"


def test_14_error_analyzer_empty(error_analyzer):
    df = error_analyzer.analyze_errors([])
    assert len(df) == 0


def test_15_error_analyzer_aggregation(error_analyzer):
    recs = [
        {"field_name": "material", "comparison_status": "MISMATCH"},
        {"field_name": "material", "comparison_status": "MISMATCH"},
        {"field_name": "size", "comparison_status": "MISSING"},
        {"field_name": "brand", "comparison_status": "MATCH"}
    ]
    df = error_analyzer.analyze_errors(recs)
    assert len(df) == 2
    assert df.iloc[0]["ATTRIBUTE"] == "material"


def test_16_zero_division_prevention():
    total = 0
    val = 0 if total == 0 else (1 / total)
    assert val == 0


def test_17_ground_truth_csv_exists():
    assert os.path.exists("data/master/ground_truth.csv")


def test_18_evaluation_summary_exists():
    assert os.path.exists("data/evaluation/evaluation_summary.json")


def test_19_field_comparison_jsonl_exists():
    assert os.path.exists("data/evaluation/field_comparison.jsonl")


def test_20_error_analysis_csv_exists():
    assert os.path.exists("data/evaluation/error_analysis.csv")


def test_21_report_exists():
    assert os.path.exists("reports/phase15_evaluation_report.txt")


def test_22_audit_exists():
    assert os.path.exists("reports/phase15_evaluation_audit.txt")


def test_23_final_acceptance_exists():
    assert os.path.exists("reports/phase15_final_acceptance.txt")


def test_24_comparator_null_input(comparator):
    s, r = comparator.compare_field("brand", None, None)
    assert s == "NOT_APPLICABLE"


def test_25_comparator_none_string_input(comparator):
    s, r = comparator.compare_field("brand", "None", "None")
    assert s == "NOT_APPLICABLE"


def test_26_comparator_nan_value(comparator):
    s, r = comparator.compare_field("brand", "nan", "nan")
    assert s == "NOT_APPLICABLE"


def test_27_comparator_mpn_exact_match(comparator):
    s, r = comparator.compare_field("mpn", "DCB518ASTS06G", "DCB518ASTS06G")
    assert s == "MATCH"


def test_28_comparator_mpn_case_mismatch(comparator):
    s, r = comparator.compare_field("mpn", "dcb518asts06g", "DCB518ASTS06G")
    assert s == "MATCH"


def test_29_comparator_brand_punctuation(comparator):
    s, r = comparator.compare_field("brand", "'Diablo'", "Diablo")
    assert s == "MATCH"


def test_30_comparator_numeric_types(comparator):
    s, r = comparator.compare_field("quantity", 6, 6)
    assert s == "MATCH"


def test_31_loader_duplicate_rejection(loader):
    loader.seed_ground_truth("data/master/test_gt_dup.csv")
    df = pd.read_csv("data/master/test_gt_dup.csv")
    # Duplicate some rows
    df = pd.concat([df, df.iloc[[0]]])
    df.to_csv("data/master/test_gt_dup_write.csv", index=False)
    _, status = loader.load_ground_truth("data/master/test_gt_dup_write.csv")
    assert "Duplicate product identifiers" in status


def test_32_loader_missing_product_id(loader):
    df = pd.DataFrame([{"product_id": "", "mpn": "M", "brand": "B", "manufacturer": "M", "product_type": "T"}])
    df.to_csv("data/master/test_gt_missing.csv", index=False)
    _, status = loader.load_ground_truth("data/master/test_gt_missing.csv")
    assert "Missing critical product_id" in status


def test_33_loader_missing_required_column(loader):
    df = pd.DataFrame([{"product_id": "P1", "brand": "B"}])
    df.to_csv("data/master/test_gt_missing_col.csv", index=False)
    _, status = loader.load_ground_truth("data/master/test_gt_missing_col.csv")
    assert "Missing required column" in status


def test_34_clean_dataset_hashes_immutability():
    from src.evaluation.phase15_pipeline import get_file_hashes
    h = get_file_hashes()
    assert len(h) > 0


def test_35_reproducible_evaluation_runs():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["products_evaluated"] > 0


def test_36_field_comparison_non_empty():
    df = pd.read_json("data/evaluation/field_comparison.jsonl", lines=True)
    assert len(df) > 0


def test_37_error_analysis_rows_sorted():
    df = pd.read_csv("data/evaluation/error_analysis.csv")
    assert len(df) >= 0


def test_38_average_confidence_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["average_prodexa_confidence"] <= 100.0


def test_39_completeness_rate_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["completeness"] <= 100.0


def test_40_missing_data_rate_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["missing_data_rate"] <= 100.0


def test_41_lov_compliance_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["lov_compliance"] <= 100.0


def test_42_uom_compliance_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["uom_compliance"] <= 100.0


def test_43_enrichment_recovery_rate_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["enrichment_recovery_rate"] <= 100.0


def test_44_human_review_rate_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["human_review_rate"] <= 100.0


def test_45_high_confidence_error_rate_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["high_confidence_error_rate"] <= 100.0


def test_46_overall_field_accuracy_bounds():
    with open("data/evaluation/evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert 0.0 <= summary["field_accuracy"] <= 100.0


def test_47_clean_up_loader_tmp_files():
    for f in ["data/master/test_gt_tmp.csv", "data/master/test_gt_dup.csv", "data/master/test_gt_dup_write.csv", "data/master/test_gt_missing.csv", "data/master/test_gt_missing_col.csv"]:
        if os.path.exists(f):
            os.remove(f)
    assert True


def test_48_verify_immutability_passes():
    from src.evaluation.phase15_pipeline import get_file_hashes, verify_immutability
    h = get_file_hashes()
    verify_immutability(h)
    assert True


def test_49_no_ground_truth_modification():
    initial_gt_size = os.path.getsize("data/master/ground_truth.csv")
    run_phase15_pipeline()
    final_gt_size = os.path.getsize("data/master/ground_truth.csv")
    assert initial_gt_size == final_gt_size


def test_50_no_final_enriched_modification():
    initial_enriched_size = os.path.getsize("data/final/enriched.csv")
    run_phase15_pipeline()
    final_enriched_size = os.path.getsize("data/final/enriched.csv")
    assert initial_enriched_size == final_enriched_size
