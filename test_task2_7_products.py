import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.understanding.schema import ProductInfo
from src.understanding.product_understanding import extract_product_info

test_descriptions = [
    '2834-21HD Milw M18 7-1/4" Circ - Saw Kit',
    'DCS383B Dewalt 20V 7-1/4" - Metal Cutting Circ Saw',
    'DCS590B Dewalt 20V Cordless - 7-1/4" Circular Saw (Bare)',
    'KPTCS725A Kreg 20V Ionic 7-1/4" Circ Saw',
    '2545-20 Milw M12 Jig Saw',
    'KPTJS100A Kreg 20V Ionic Barrel Grip Jigsaw',
    'DCB2108-2 Dewalt 20V 8Ah 2pk - Battery Max XR Powerpack'
]

print("=" * 80)
print("TASK 2 — DIRECT EXTRACTION TEST ON 7 SPECIFIED PRODUCTS")
print("=" * 80)

for idx, desc in enumerate(test_descriptions, 1):
    print(f"\n[{idx}] RAW DESCRIPTION: {desc}")
    
    validation_error = None
    info_obj, status = extract_product_info(desc)
    
    raw_json_str = info_obj.model_dump_json(indent=2)
    print("PARSED JSON / PYDANTIC RESULT:")
    print(raw_json_str)
    print(f"VALIDATION ERROR: {validation_error}")
    print(f"FINAL STATUS: {status.upper()} (Confidence: {info_obj.confidence})")
    print("-" * 80)
