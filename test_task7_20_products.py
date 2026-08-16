import sys
import json
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.understanding.product_understanding import extract_product_info

sample_20_descriptions = [
    '2834-21HD Milw M18 7-1/4" Circ - Saw Kit',
    'DCS383B Dewalt 20V 7-1/4" - Metal Cutting Circ Saw',
    '2545-20 Milw M12 Jig Saw',
    'KPTJS100A Kreg 20V Ionic Barrel Grip Jigsaw',
    'DCB2108-2 Dewalt 20V 8Ah 2pk - Battery Max XR Powerpack',
    '48-59-1812 Milw M18 & M12 Rapid Charger',
    '48-22-8424 Milw PACKOUT Tool Box Organizer',
    'DCP580B Dewalt 20V Max 3-1/4" Brushless Planer',
    'DWE74911 Dewalt Heavy Duty Rolling Table Saw Stand/Fence',
    'DWV012 Dewalt 10 Gallon Dust Extractor',
    'DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc',
    '3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box',
    '5B-332-080 HIOLIT 5" P80',
    '9A-570-240 Abranet 2.75x30',
    '49-94-0013 Milw 5"x.045"x7/8" Metal Cut Off Disc',
    'DBD090094101F Diablo 9" - Metal Cut-Off Disc',
    '49-94-0501 Milw 4"x1/4"x5/8" Metal Grinding Wheel',
    'DFBLBLOMFN01G Diablo 220 Grit - Flat Edge Sanding Disc',
    '3/4x60\' Vinyl Elect Tape',
    'KDTS324SPS Kitchen Aid Dishwasher SS'
]

print("=" * 80)
print("TASK 7 — 20-PRODUCT DEBUG TEST ACROSS REPRESENTATIVE CATEGORIES")
print("=" * 80)

status_counts = {"success": 0, "partial": 0, "failed": 0}

for idx, desc in enumerate(sample_20_descriptions, 1):
    info_obj, status = extract_product_info(desc)
    status_counts[status] += 1
    
    print(f"\n[{idx:02d}] {desc}")
    print(f"     MPN: {info_obj.manufacturer_part_number} | Brand: {info_obj.brand} | Type: {info_obj.product_type} | Size: {info_obj.size} | Qty: {info_obj.quantity}")
    print(f"     STATUS: {status.upper()} (Confidence: {info_obj.confidence})")

print("\n" + "=" * 80)
print("TASK 7 SUMMARY BREAKDOWN (TARGET: Majority SUCCESS / PARTIAL, minimal FAILED)")
print("=" * 80)
for st, cnt in status_counts.items():
    pct = (cnt / len(sample_20_descriptions)) * 100
    print(f"  {st.upper()}: {cnt}/{len(sample_20_descriptions)} ({pct:.1f}%)")
