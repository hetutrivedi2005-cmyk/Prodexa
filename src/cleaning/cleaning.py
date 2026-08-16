import pandas as pd
import re
import unicodedata
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "input.csv"
OUTPUT_FILE = "cleaned_dataset.csv"

# Values that should be treated as missing
PLACEHOLDERS = {
    "",
    "null",
    "none",
    "n/a",
    "na",
    "nan",
    "unknown",
    "-- unbranded --",
    "-- no unilog brand --",
    "-- no dib brand --",
    "unbranded",
}


# ============================================================
# 1. NORMALIZE TEXT
# ============================================================

def normalize_text(value):
    """
    Basic text normalization:
    - Convert to string
    - Normalize Unicode
    - Remove unusual characters
    - Normalize whitespace
    """

    if pd.isna(value):
        return None

    value = str(value)

    # Unicode normalization
    value = unicodedata.normalize("NFKC", value)

    # Replace non-breaking spaces
    value = value.replace("\u00A0", " ")

    # Remove leading/trailing spaces
    value = value.strip()

    # Replace multiple spaces with one
    value = re.sub(r"\s+", " ", value)

    if not value:
        return None

    return value


# ============================================================
# 2. REMOVE PLACEHOLDER VALUES
# ============================================================

def remove_placeholder(value):
    """
    Convert placeholder values into None/NaN.
    """

    if value is None or pd.isna(value):
        return None

    normalized = normalize_text(value)

    if normalized is None:
        return None

    # Compare lowercase version
    check_value = normalized.lower()

    if check_value in PLACEHOLDERS:
        return None

    return normalized


# ============================================================
# 3. CLEAN MANUFACTURER NAME
# ============================================================

def clean_manufacturer(value):
    """
    Cleans manufacturer names.

    Example:
        Freud Inc (2435)
        ->
        Freud Inc

    The number inside parentheses is assumed to be an
    internal/reference code rather than part of the name.
    """

    value = remove_placeholder(value)

    if value is None:
        return None

    # Remove codes such as:
    # (2435)
    # (123)
    # (ABC123)
    value = re.sub(r"\s*\([^)]*\)\s*$", "", value)

    # Remove extra whitespace
    value = re.sub(r"\s+", " ", value).strip()

    return value


# ============================================================
# 4. STANDARDIZE GENERAL STRINGS
# ============================================================

def standardize_string(value):
    """
    Standardize normal text fields.
    """

    value = remove_placeholder(value)

    if value is None:
        return None

    # Normalize punctuation spacing
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# 5. LOAD CSV
# ============================================================

def load_dataset(file_path):
    print(f"\n📂 Loading dataset: {file_path}")

    df = pd.read_csv(
        file_path,
        encoding="utf-8",
        low_memory=False
    )

    print(f"✅ Loaded {len(df)} rows")
    print(f"📊 Columns: {len(df.columns)}")

    return df


# ============================================================
# 6. CLEAN DATASET
# ============================================================

def clean_dataset(df):

    print("\n🧹 Starting data cleaning...")

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    print("✅ Column names normalized")

    # --------------------------------------------------------
    # Clean every column
    # --------------------------------------------------------

    for column in df.columns:

        df[column] = df[column].apply(standardize_string)

    print("✅ Basic string cleaning completed")

    # --------------------------------------------------------
    # Detect manufacturer column
    # --------------------------------------------------------

    manufacturer_columns = [
        "manufacturer",
        "manufacturer_name",
        "mfr",
        "brand",
        "brand_name"
    ]

    manufacturer_column = None

    for column in manufacturer_columns:
        if column in df.columns:
            manufacturer_column = column
            break

    if manufacturer_column:

        print(
            f"🏭 Cleaning manufacturer column: "
            f"{manufacturer_column}"
        )

        df[manufacturer_column] = (
            df[manufacturer_column]
            .apply(clean_manufacturer)
        )

    else:

        print("⚠️ Manufacturer column not found")

    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    before = len(df)

    df = df.dropna(how="all")

    removed = before - len(df)

    print(f"🗑️ Removed {removed} completely empty rows")

    # --------------------------------------------------------
    # Detect duplicate rows
    # --------------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print(f"🔍 Duplicate rows found: {duplicate_count}")

    if duplicate_count > 0:
        df = df.drop_duplicates()

        print(
            f"🗑️ Removed {duplicate_count} duplicate rows"
        )

    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    df = df.reset_index(drop=True)

    return df


# ============================================================
# 7. DATA QUALITY REPORT
# ============================================================

def generate_quality_report(df):

    print("\n" + "=" * 60)
    print("📊 DATA QUALITY REPORT")
    print("=" * 60)

    print(f"\nTotal rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nMissing values:")

    missing = df.isna().sum()

    for column, count in missing.items():

        if count > 0:
            percentage = (count / len(df)) * 100

            print(
                f"  {column}: "
                f"{count} ({percentage:.2f}%)"
            )

    print("\nColumn types:")

    print(df.dtypes)

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("=" * 60)


# ============================================================
# 8. SAVE CLEAN DATASET
# ============================================================

def save_dataset(df, output_file):

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(f"\n💾 Clean dataset saved to:")
    print(f"   {output_file}")


# ============================================================
# 9. MAIN PIPELINE
# ============================================================

def main():

    print("=" * 60)
    print("🚀 PRODEXA DATA CLEANING ENGINE")
    print("=" * 60)

    # Load
    df = load_dataset(INPUT_FILE)

    # Show original sample
    print("\n🔎 Original data:")
    print(df.head())

    # Clean
    df = clean_dataset(df)

    # Quality report
    generate_quality_report(df)

    # Show cleaned sample
    print("\n✨ Cleaned data:")
    print(df.head())

    # Save
    save_dataset(df, OUTPUT_FILE)

    print("\n✅ PHASE 1 COMPLETED!")
    print("➡️ Clean dataset is ready for Phase 2.")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()