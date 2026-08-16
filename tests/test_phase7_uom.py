import os
import pytest
import pandas as pd
from src.understanding.uom_normalizer import UOMNormalizer
from src.understanding.phase7_pipeline import run_phase7_pipeline
from src.understanding.uom_validator import validate_phase7_output


@pytest.fixture(scope="module")
def normalizer():
    return UOMNormalizer()


def test_1_24_inches_to_24_in(normalizer):
    res = normalizer.normalize("24 inches", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "24 in"
    assert res["uom"] == "in"


def test_2_24_in_punct_to_24_in(normalizer):
    res = normalizer.normalize("24 IN.", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "24 in"


def test_3_24in_no_space_to_24_in(normalizer):
    res = normalizer.normalize("24in", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "24 in"


def test_4_0_5_in_to_half_in(normalizer):
    res = normalizer.normalize("0.5 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "1/2 in"


def test_5_0_25_in_to_quarter_in(normalizer):
    res = normalizer.normalize("0.25 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "1/4 in"


def test_6_0_75_in_to_three_quarter_in(normalizer):
    res = normalizer.normalize("0.75 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "3/4 in"


def test_7_0_375_in_to_three_eighths_in(normalizer):
    res = normalizer.normalize("0.375 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "3/8 in"


def test_8_50_25_in_to_50_quarter_in(normalizer):
    res = normalizer.normalize("50.25 in", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "50-1/4 in"


def test_9_1_5_in_to_1_half_in(normalizer):
    res = normalizer.normalize("1.5 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "1-1/2 in"


def test_10_2_3_8_in_passthrough(normalizer):
    res = normalizer.normalize("2 3/8 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "2-3/8 in"


def test_11_1_2_in_passthrough(normalizer):
    res = normalizer.normalize("1/2 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "1/2 in"


def test_12_3_8_in_passthrough(normalizer):
    res = normalizer.normalize("3/8 in", "diameter")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "3/8 in"


def test_13_compound_5_by_18(normalizer):
    res = normalizer.normalize('5"x18"', "dimensions")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "5 in x 18 in"


def test_14_compound_triple_dimension(normalizer):
    res = normalizer.normalize('5"x1/8"x7/8"', "dimensions")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "5 in x 1/8 in x 7/8 in"


def test_15_uppercase_unit(normalizer):
    res = normalizer.normalize("5 INCH", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "5 in"


def test_16_lowercase_unit(normalizer):
    res = normalizer.normalize("5 inch", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "5 in"


def test_17_unit_with_punctuation(normalizer):
    res = normalizer.normalize("5 in.", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "5 in"


def test_18_millimeter_normalization(normalizer):
    res = normalizer.normalize("20 MM", "arbor_size")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "20 mm"
    assert res["uom"] == "mm"


def test_19_feet_normalization(normalizer):
    res = normalizer.normalize("10 feet", "length")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "10 ft"
    assert res["uom"] == "ft"


def test_20_voltage_normalization(normalizer):
    res = normalizer.normalize("20V", "voltage")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "20 V"
    assert res["uom"] == "V"


def test_21_wattage_normalization(normalizer):
    res = normalizer.normalize("60W", "wattage")
    assert res["status"] == "normalized"
    assert res["normalized_value"] == "60 W"
    assert res["uom"] == "W"


def test_22_unsupported_unit_rejection(normalizer):
    res = normalizer.normalize("15 xyz", "length")
    assert res["status"] == "unresolved"
    assert res["method"] == "unsupported_unit"
    assert res["normalized_value"] is None


def test_23_invalid_value_rejection(normalizer):
    res = normalizer.normalize("UNAPPROVED_VALUE", "length")
    assert res["status"] == "unresolved"
    assert res["method"] == "unsupported"
    assert res["normalized_value"] is None


def test_24_uom_master_validation(normalizer):
    assert "in" in normalizer.canonical_uom_set
    assert "mm" in normalizer.canonical_uom_set
    assert "V" in normalizer.canonical_uom_set
    assert "W" in normalizer.canonical_uom_set


def test_25_unsupported_attribute_handling(normalizer):
    res = normalizer.normalize("P150", "grit")
    assert res["status"] == "normalized"
    assert res["method"] == "already_canonical"
    assert res["normalized_value"] == "P150"


def test_26_fraction_precision(normalizer):
    res = normalizer.normalize("0.125 in", "diameter")
    assert res["normalized_value"] == "1/8 in"


def test_27_compound_dimension_parsing_without_context(normalizer):
    # Without length/dimension context, missing units are NOT guessed!
    res = normalizer.normalize("2.75x30", "unknown_attribute")
    assert res["status"] == "unresolved"


def test_28_no_semantic_unit_conversion(normalizer):
    res = normalizer.normalize("5 in", "length")
    assert res["normalized_value"] == "5 in"
    assert res["uom"] == "in"


def test_29_phase6_column_preservation():
    df_p6 = pd.read_csv("data/processed/lov_resolved_products.csv")
    df_p7 = pd.read_csv("data/processed/uom_normalized_products.csv")
    for col in df_p6.columns:
        assert col in df_p7.columns


def test_30_row_count_preservation():
    df_p6 = pd.read_csv("data/processed/lov_resolved_products.csv")
    df_p7 = pd.read_csv("data/processed/uom_normalized_products.csv")
    assert len(df_p7) == len(df_p6) == 1000


def test_31_adversarial_numeric_distinction_5(normalizer):
    res = normalizer.normalize("5", "pack_quantity")
    assert res["normalized_value"] == "5"


def test_32_adversarial_numeric_distinction_50(normalizer):
    res = normalizer.normalize("50", "pack_quantity")
    assert res["normalized_value"] == "50"


def test_33_adversarial_numeric_distinction_5_point_0(normalizer):
    res = normalizer.normalize("5.0", "pack_quantity")
    assert res["normalized_value"] == "5"


def test_34_adversarial_numeric_distinction_50_point_0(normalizer):
    res = normalizer.normalize("50.0", "pack_quantity")
    assert res["normalized_value"] == "50"


def test_35_adversarial_numeric_distinction_5_in(normalizer):
    res = normalizer.normalize("5 in", "diameter")
    assert res["normalized_value"] == "5 in"


def test_36_adversarial_numeric_distinction_50_in(normalizer):
    res = normalizer.normalize("50 in", "length")
    assert res["normalized_value"] == "50 in"
