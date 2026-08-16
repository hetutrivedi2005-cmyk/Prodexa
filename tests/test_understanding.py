import pytest
from unittest.mock import MagicMock
import pandas as pd
from pydantic import ValidationError

from src.understanding.schema import ProductInfo, clean_string_value
from src.understanding.normalizer import ProductNormalizer
from src.understanding.product_understanding import (
    extract_product_info,
    detect_description_column,
    process_csv
)


# ============================================================================
# 1. MARKDOWN STRIPPING & NULL SANITIZATION
# ============================================================================
def test_markdown_stripping_and_null_sanitization():
    assert clean_string_value("**Sanding Belt**") == "Sanding Belt"
    assert clean_string_value("**5 in**") == "5 in"
    assert clean_string_value("**2.75 in x 30 in**") == "2.75 in x 30 in"
    assert clean_string_value("`Abrasive Disc`") == "Abrasive Disc"
    assert clean_string_value("**") is None
    assert clean_string_value("null") is None
    assert clean_string_value("N/A") is None
    assert clean_string_value("none") is None

    info = ProductInfo(
        manufacturer_part_number="**DCB518ASTS06G**",
        brand="**Diablo**",
        product_type="**Sanding Belt**",
        size="**1/2 in x 18 in**",
        quantity=6
    )
    assert info.manufacturer_part_number == "DCB518ASTS06G"
    assert info.brand == "Diablo"
    assert info.product_type == "Sanding Belt"
    assert info.size == "1/2 in x 18 in"


# ============================================================================
# 2. REQUIRED TEST 1: DCB518ASTS06G Diablo
# ============================================================================
def test_product_dcb518asts06g():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"manufacturer_part_number": "DCB518ASTS06G", "brand": "Diablo", "product_type": "Sanding Belt", "size": "1/2 in x 18 in", "quantity": 6}'
    mock_client.models.generate_content.return_value = mock_response

    info, status = extract_product_info(
        description='DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc',
        client=mock_client
    )

    assert status == "success"
    assert info.manufacturer_part_number == "DCB518ASTS06G"
    assert info.brand == "Diablo"
    assert info.product_type == "Sanding Belt"
    assert info.size == "1/2 in x 18 in"
    assert info.quantity == 6
    assert info.confidence >= 0.85


# ============================================================================
# 3. REQUIRED TEST 2, 3, 4: 3M 775L Stikit Film & Batch Consistency
# ============================================================================
def test_product_3m_775l_series_and_batch_consistency():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"manufacturer_part_number": "775L", "brand": "3M", "product_type": "Stikit Film Disc", "size": null, "quantity": 50}'
    mock_client.models.generate_content.return_value = mock_response

    info, status = extract_product_info(
        description='3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box',
        client=mock_client
    )

    assert status in ["success", "partial"]
    assert info.manufacturer_part_number == "775L"
    assert info.brand == "3M"
    assert info.product_type == "Stikit Film Disc"
    assert info.quantity == 50

    # Test Batch Product Type Consistency
    batch_input = [
        (ProductInfo(manufacturer_part_number="775L", brand="3M", product_type="Stikit Film Disc", quantity=50), "3M 775L Stikit Film P150 50 Disc/Box"),
        (ProductInfo(manufacturer_part_number="775L", brand="3M", product_type="Disc", quantity=50), "3M 775L Stikit Film P180 50 Disc/Box"),
        (ProductInfo(manufacturer_part_number="775L", brand="3M", product_type=None, quantity=50), "3M 775L Stikit Film P220 50 Disc/Box")
    ]

    normalized_batch = ProductNormalizer.normalize_batch_consistency(batch_input)
    for norm_info, _ in normalized_batch:
        assert norm_info.product_type == "Stikit Film Disc"


# ============================================================================
# 4. REQUIRED TEST 5: 5B-332-080 HIOLIT 5" P80 (Status = Success via Fallback)
# ============================================================================
def test_product_5b_332_080():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"manufacturer_part_number": "5B-332-080", "brand": "HIOLIT", "product_type": null, "size": "5 in", "quantity": null}'
    mock_client.models.generate_content.return_value = mock_response

    info, status = extract_product_info(
        description='5B-332-080 HIOLIT 5" P80',
        client=mock_client
    )

    assert status == "success"
    assert info.manufacturer_part_number == "5B-332-080"
    assert info.brand == "HIOLIT"
    assert info.product_type == "Abrasive Disc"
    assert info.size == "5 in"
    assert info.quantity is None  # P80 is grit, NOT quantity!


# ============================================================================
# 5. REQUIRED TEST 6: 5B-332-120 HIOLIT 5" P120
# ============================================================================
def test_product_5b_332_120():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"manufacturer_part_number": "5B-332-120", "brand": "HIOLIT", "product_type": null, "size": "5 in", "quantity": null}'
    mock_client.models.generate_content.return_value = mock_response

    info, status = extract_product_info(
        description='5B-332-120 HIOLIT 5" P120',
        client=mock_client
    )

    assert status == "success"
    assert info.manufacturer_part_number == "5B-332-120"
    assert info.brand == "HIOLIT"
    assert info.product_type == "Abrasive Disc"
    assert info.size == "5 in"
    assert info.quantity is None


# ============================================================================
# 6. REQUIRED TEST 7: 9A-570-240 Abranet 2.75x30
# ============================================================================
def test_product_9a_570_240():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"manufacturer_part_number": "9A-570-240", "brand": "Abranet", "product_type": null, "size": "2.75 in x 30 in", "quantity": null}'
    mock_client.models.generate_content.return_value = mock_response

    info, status = extract_product_info(
        description='9A-570-240 Abranet 2.75x30',
        client=mock_client
    )

    assert status == "success"
    assert info.manufacturer_part_number == "9A-570-240"
    assert info.brand == "Abranet"
    assert info.product_type == "Abrasive Mesh Strip"
    assert info.size == "2.75 in x 30 in"
    assert info.quantity is None


# ============================================================================
# 7. CONFIDENCE SCORE & STATUS LOGIC
# ============================================================================
def test_confidence_and_status_logic():
    # Complete explicit item -> success (conf >= 0.85)
    full_info = ProductInfo(
        manufacturer_part_number="MPN123",
        brand="BrandX",
        product_type="Belt",
        size="10 in",
        quantity=5
    )
    conf1, status1 = ProductNormalizer.compute_confidence_and_status(full_info, "Full Item Description")
    assert conf1 >= 0.85
    assert status1 == "success"

    # Partial item -> partial (0.50 <= conf < 0.85)
    part_info = ProductInfo(
        manufacturer_part_number="MPN123",
        brand="BrandX",
        size="10 in"
    )
    conf2, status2 = ProductNormalizer.compute_confidence_and_status(part_info, "Partial Description")
    assert 0.50 <= conf2 < 0.85
    assert status2 == "partial"

    # Empty item -> failed
    empty_info = ProductInfo()
    conf3, status3 = ProductNormalizer.compute_confidence_and_status(empty_info, "")
    assert conf3 == 0.0
    assert status3 == "failed"


# ============================================================================
# 8. COLUMN DETECTION
# ============================================================================
def test_column_detection():
    variants = [
        ("product_description", pd.DataFrame(columns=["id", "product_description", "price"])),
        ("description", pd.DataFrame(columns=["id", "DESCRIPTION"])),
        ("part_desc", pd.DataFrame(columns=["mfg_part_num", "part_desc", "brand"])),
        ("item_description", pd.DataFrame(columns=["item_description"]))
    ]

    for expected_name, df in variants:
        detected = detect_description_column(df)
        assert detected.lower().strip() == expected_name.lower().strip()

    bad_df = pd.DataFrame(columns=["col1", "col2"])
    with pytest.raises(ValueError, match="Could not find a valid product description column"):
        detect_description_column(bad_df)
