import os
import re
os.environ["GLOG_minloglevel"] = "2"
os.environ["GRPC_VERBOSITY"] = "ERROR"

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import time
import logging
import argparse
from typing import Optional, Dict, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.errors import APIError

from src.understanding.schema import ProductInfo, clean_value, clean_string_value
from src.understanding.normalizer import ProductNormalizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Prodexa.Understanding")
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("absl").setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
CANDIDATE_MODELS = [DEFAULT_MODEL, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest"]
DEFAULT_REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2.0"))

SYSTEM_INSTRUCTION = """
You are an expert product attribute extraction engine.
Extract only information explicitly present or strongly supported by the raw product description.

IMPORTANT PRINCIPLE: HIGH PRECISION > HIGH RECALL
If a value is not explicitly present or strongly implied, return null. Never guess or hallucinate.

Rules:
1. Never hallucinate. Never invent missing information.
2. Markdown formatting (like **bold** or `code` markers) must NEVER be used in returned string values. Return plain text only.
3. Preserve the actual manufacturer part number (MPN) or model code as-is.
4. BRAND EXTRACTION:
   - Extract the brand explicitly present in the product description (e.g., "HIOLIT" for "5B-332-080 HIOLIT 5\" P80", "Abranet" for "9A-570-240 Abranet 2.75x30", "3M" for "3M 775L...", "Diablo" for "Diablo...").
   - Do not guess or invent a brand if none is present in the description.
5. ABRASIVE GRIT RATINGS ARE NOT QUANTITIES:
   - Examples of grit ratings: P40, P60, P80, P120, P150, P180, P220, P320.
   - These are grit specifications, NOT package quantities! For descriptions like "P80" or "HIOLIT 5\" P80", quantity MUST be null.
6. EXAMPLES OF PACKAGE QUANTITIES:
   - "6pc" -> 6
   - "6 pcs" -> 6
   - "50 Disc/Box" -> 50
   - "50 discs per box" -> 50
   - "5 pack" -> 5
   - "PK10" -> 10
   - Quantity should only be extracted when the description clearly indicates a package item count. Otherwise, return null.
7. DIMENSION NORMALIZATION:
   - Normalize obvious dimensions conservatively into readable formats:
     "1/2\"x18\"" -> "1/2 in x 18 in"
     "5\"" -> "5 in"
     "2.75x30" -> "2.75 in x 30 in"
   - Do NOT confuse grit, model number, part number, or quantity with dimensions.
   - Do not invent dimensions.
8. PRODUCT TYPES:
   - Infer the most descriptive product type supported by the description when explicitly indicated:
     "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box" -> product_type: "Stikit Film Disc"
     "DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc" -> product_type: "Sanding Belt"
   - If product_type is not explicitly stated in the description (e.g. for "5B-332-080 HIOLIT 5\" P80" or "9A-570-240 Abranet 2.75x30"), DO NOT invent a product type. Return null for product_type.
9. Return ONLY valid JSON matching the ProductInfo schema.
"""

COLUMN_CANDIDATES = [
    "product_description",
    "description",
    "product_name",
    "product",
    "item_description",
    "part_desc",
    "item_desc",
    "desc"
]


def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """
    Initialize and return a Google GenAI Client.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found in environment or .env file.")
    return genai.Client(api_key=key)


def detect_description_column(df: pd.DataFrame, custom_column: Optional[str] = None) -> str:
    """
    Identifies the product description column in a DataFrame based on standard candidate names.
    """
    if custom_column:
        if custom_column in df.columns:
            return custom_column
        for col in df.columns:
            if col.lower().strip() == custom_column.lower().strip():
                return col

    existing_cols_map = {col.lower().strip(): col for col in df.columns}
    for candidate in COLUMN_CANDIDATES:
        if candidate in existing_cols_map:
            return existing_cols_map[candidate]

    raise ValueError(
        f"Could not find a valid product description column. "
        f"Searched for candidates {COLUMN_CANDIDATES}. Available columns: {list(df.columns)}"
    )


def understand_product(description: str, client: Optional[genai.Client] = None) -> ProductInfo:
    """
    Extracts structured ProductInfo for a single product description string.
    """
    info, _ = extract_product_info(description, client=client)
    return info


QUOTA_EXHAUSTED_GLOBAL = False


def extract_product_info(
    description: Optional[str],
    client: Optional[genai.Client] = None,
    model_name: str = DEFAULT_MODEL,
    max_retries: int = 3,
    initial_backoff: float = 1.0
) -> Tuple[ProductInfo, str]:
    """
    Extracts structured ProductInfo from a single product description string.

    Returns:
        Tuple of (ProductInfo model, status_string)
        Status values: 'success', 'partial', 'ambiguous', 'failed'
    """
    global QUOTA_EXHAUSTED_GLOBAL

    if description is None or pd.isna(description):
        info = ProductInfo(understanding_status="failed", confidence=0.0)
        return info, "failed"

    cleaned_desc = str(description).strip()
    if not cleaned_desc:
        info = ProductInfo(understanding_status="failed", confidence=0.0)
        return info, "failed"

    # Always check deterministic fallback extractor first/in parallel
    fallback_info = ProductNormalizer.deterministic_fallback_extract(cleaned_desc)

    extracted_info: Optional[ProductInfo] = None

    if client is None and not QUOTA_EXHAUSTED_GLOBAL:
        try:
            client = get_gemini_client()
        except Exception as e:
            logger.warning(f"Could not initialize Gemini client: {e}. Relying on deterministic fallback.")

    if client is not None and not QUOTA_EXHAUSTED_GLOBAL:
        prompt = f"Product Description: {cleaned_desc}"
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ProductInfo,
            temperature=0.0,
            system_instruction=SYSTEM_INSTRUCTION,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )

        candidate_list = [model_name] + [m for m in CANDIDATE_MODELS if m != model_name]

        for current_model in candidate_list:
            if QUOTA_EXHAUSTED_GLOBAL:
                break
            for attempt in range(1, max_retries + 1):
                try:
                    response = client.models.generate_content(
                        model=current_model,
                        contents=prompt,
                        config=config
                    )

                    response_text = response.text if response and response.text else None
                    if not response_text:
                        raise ValueError("Empty response received from Gemini API.")

                    extracted_info = ProductInfo.model_validate_json(response_text)
                    break
                except APIError as e:
                    err_msg = str(e)
                    if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg or "Quota exceeded" in err_msg:
                        logger.warning(f"Rate limit / Quota exceeded on {current_model}. Using fallback extractor for remaining batch.")
                        QUOTA_EXHAUSTED_GLOBAL = True
                        break
                    else:
                        backoff = initial_backoff * (2 ** (attempt - 1))
                        logger.warning(f"Gemini API attempt {attempt}/{max_retries} on {current_model} failed for '{cleaned_desc[:30]}...': {e}")
                except Exception as e:
                    backoff = initial_backoff * (2 ** (attempt - 1))
                    logger.warning(f"Extraction attempt {attempt}/{max_retries} on {current_model} failed for '{cleaned_desc[:30]}...': {e}")

                if attempt < max_retries:
                    time.sleep(backoff)

            if extracted_info is not None or QUOTA_EXHAUSTED_GLOBAL:
                break

    # If Gemini extraction failed or is incomplete, integrate with deterministic fallback
    if extracted_info is None:
        if fallback_info is not None:
            extracted_info = fallback_info
        else:
            failed_info = ProductInfo(understanding_status="failed", confidence=0.0)
            return failed_info, "failed"
    else:
        # Merge fields from fallback if Gemini missed critical attributes
        if fallback_info is not None:
            if not extracted_info.manufacturer_part_number and fallback_info.manufacturer_part_number:
                extracted_info.manufacturer_part_number = fallback_info.manufacturer_part_number
            if not extracted_info.brand and fallback_info.brand:
                extracted_info.brand = fallback_info.brand
            if not extracted_info.product_type and fallback_info.product_type:
                extracted_info.product_type = fallback_info.product_type
            if not extracted_info.size and fallback_info.size:
                extracted_info.size = fallback_info.size

    sanitized_info = ProductNormalizer.sanitize_attributes(extracted_info, cleaned_desc)
    conf, status = ProductNormalizer.compute_confidence_and_status(sanitized_info, cleaned_desc)
    sanitized_info.confidence = conf
    sanitized_info.understanding_status = status

    if status == "failed":
        logger.warning(f"[{status.upper()}] '{cleaned_desc[:40]}' - Confidence: {conf}")
    else:
        logger.info(f"[{status.upper()}] '{cleaned_desc[:40]}' - Confidence: {conf}")

    return sanitized_info, status


def process_csv(
    input_path: str = "data/processed/cleaned_dataset.csv",
    output_path: str = "data/processed/understood_products.csv",
    description_column: Optional[str] = None,
    client: Optional[genai.Client] = None,
    model_name: str = DEFAULT_MODEL,
    max_workers: int = 1,
    limit: Optional[int] = None,
    request_delay: float = DEFAULT_REQUEST_DELAY
) -> pd.DataFrame:
    """
    Main processing pipeline for Phase 2.
    Reads input CSV, detects description column, uses deduplicated LLM calls + fallback to extract product info,
    applies batch product-type consistency normalization, hard-cleans all columns and values, performs pre-save assertions, and saves output CSV.
    """
    print("[INFO] Loading dataset...")
    in_file = Path(input_path)
    if not in_file.exists():
        raw_fallback = Path("data/raw/input.csv")
        if raw_fallback.exists():
            print(f"[INFO] Cleaned dataset not found at {input_path}. Falling back to {raw_fallback}")
            in_file = raw_fallback
        else:
            raise FileNotFoundError(f"Input file not found at {input_path} or {raw_fallback}")

    df = pd.read_csv(in_file, encoding="utf-8", low_memory=False)

    target_col = detect_description_column(df, custom_column=description_column)
    print(f"[INFO] Found product description column: {target_col}")

    if limit and limit > 0:
        print(f"[INFO] Limiting processing to first {limit} rows.")
        df = df.head(limit).copy()

    cache: Dict[str, ProductInfo] = {}
    unique_descriptions = df[target_col].dropna().unique()
    print(f"[INFO] Unique descriptions: {len(unique_descriptions)}")

    if client is None:
        try:
            client = get_gemini_client()
        except Exception as e:
            print(f"[WARNING] Gemini client not initialized ({e}). Pipeline will rely on deterministic fallback.")
            client = None

    print(f"[INFO] Processing products (pacing delay: {request_delay}s per request)...")

    uncached_descriptions: List[str] = []
    for raw_desc in unique_descriptions:
        desc_str = str(raw_desc).strip()
        if not desc_str:
            cache[desc_str] = ProductInfo(understanding_status="failed", confidence=0.0)
        else:
            uncached_descriptions.append(desc_str)

    if uncached_descriptions:
        total_uncached = len(uncached_descriptions)
        raw_results: List[Tuple[ProductInfo, str]] = []

        completed_count = 0
        for desc_str in uncached_descriptions:
            info_obj, status = extract_product_info(
                description=desc_str,
                client=client,
                model_name=model_name
            )
            raw_results.append((info_obj, desc_str))
            completed_count += 1

            if completed_count % 10 == 0 or completed_count == total_uncached:
                print(f"[INFO] Progress: {completed_count}/{total_uncached} unique descriptions processed...")

            if request_delay > 0 and completed_count < total_uncached and client is not None:
                time.sleep(request_delay)

        # Apply batch consistency normalization layer
        normalized_batch = ProductNormalizer.normalize_batch_consistency(raw_results)
        for norm_info, desc_str in normalized_batch:
            cache[desc_str] = norm_info

    # Map cached results onto DataFrame rows
    extracted_rows = []
    success_count = 0
    partial_count = 0
    ambiguous_count = 0
    failed_count = 0

    for val in df[target_col]:
        desc_key = str(val).strip() if pd.notna(val) else str(val)
        if desc_key in cache:
            info_obj = cache[desc_key]
        else:
            info_obj = ProductInfo(understanding_status="failed", confidence=0.0)

        info_dict = info_obj.model_dump()
        extracted_rows.append(info_dict)

        st = info_obj.understanding_status
        if st == "success":
            success_count += 1
        elif st == "partial":
            partial_count += 1
        elif st == "ambiguous":
            ambiguous_count += 1
        else:
            failed_count += 1

    print(f"[INFO] Successfully processed (Success): {success_count}")
    print(f"[INFO] Partially processed (Partial): {partial_count}")
    if ambiguous_count > 0:
        print(f"[INFO] Ambiguous: {ambiguous_count}")
    print(f"[INFO] Failed: {failed_count}")

    extracted_df = pd.DataFrame(extracted_rows)

    # Attach Phase 2 columns to primary DataFrame
    phase2_fields = ["manufacturer_part_number", "brand", "product_type", "size", "quantity", "understanding_status", "confidence"]
    for col in phase2_fields:
        if col in extracted_df.columns:
            df[col] = extracted_df[col]

    # =========================================================================
    # HARD CLEANING OF DATAFRAME BEFORE SAVING
    # =========================================================================

    # 1. Hard-clean ALL column names
    clean_columns_map = {}
    for col in df.columns:
        cleaned_col = str(col).replace("*", "").replace("`", "").strip()
        cleaned_col = re.sub(r"\s+", " ", cleaned_col)
        clean_columns_map[col] = cleaned_col
    df.rename(columns=clean_columns_map, inplace=True)

    # 2. Hard-clean string value columns
    string_cols = ["manufacturer_part_number", "brand", "product_type", "size"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_value)

    # 3. Clean quantity column cleanly to integer string or empty string
    if "quantity" in df.columns:
        def clean_qty(v):
            if pd.isna(v) or v is None or str(v).strip().lower() in ["", "nan", "none", "<na>"]:
                return ""
            try:
                val_num = int(float(str(v).strip()))
                return str(val_num) if val_num >= 1 else ""
            except Exception:
                return ""

        df["quantity"] = df["quantity"].apply(clean_qty)

    # 4. Clean understanding_status column
    if "understanding_status" in df.columns:
        df["understanding_status"] = df["understanding_status"].apply(lambda v: clean_value(v) or "failed")

    # =========================================================================
    # PRE-SAVE MANDATORY ASSERTIONS
    # =========================================================================
    assert not any("*" in str(col) for col in df.columns), f"Column names contain '*': {[col for col in df.columns if '*' in str(col)]}"
    assert not any("`" in str(col) for col in df.columns), f"Column names contain backticks: {[col for col in df.columns if '`' in str(col)]}"

    check_string_df = df[string_cols].fillna("").astype(str)
    has_asterisk = check_string_df.apply(lambda x: x.str.contains(r"\*", regex=True)).any().any()
    assert not has_asterisk, "Extracted string values contain '*'"

    has_backtick = check_string_df.apply(lambda x: x.str.contains(r"`", regex=True)).any().any()
    assert not has_backtick, "Extracted string values contain backticks"

    print("[INFO] All pre-save quality assertions passed cleanly!")
    print("[INFO] Saving results...")
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")

    print("[INFO] Phase 2 completed successfully!")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prodexa Phase 2 Product Understanding Engine")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows to process")
    parser.add_argument("--delay", type=float, default=DEFAULT_REQUEST_DELAY, help="Request pacing delay in seconds (default 2.0s for Free Tier 15 RPM)")
    parser.add_argument("--input", type=str, default="data/processed/cleaned_dataset.csv", help="Input CSV path")
    parser.add_argument("--output", type=str, default="data/processed/understood_products.csv", help="Output CSV path")
    args = parser.parse_args()

    process_csv(
        input_path=args.input,
        output_path=args.output,
        limit=args.limit,
        request_delay=args.delay
    )
