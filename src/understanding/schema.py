import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Recognized null / placeholder values
PLACEHOLDERS = {
    "", "null", "none", "n/a", "na", "nan", "unknown", "not available",
    "-- unbranded --", "-- no unilog brand --", "-- no dib brand --",
    "unbranded", "**", "*", "`"
}


def clean_value(val: Optional[str]) -> Optional[str]:
    """
    Hard-cleans extracted string values:
    - Return None for None / NaN
    - Convert value to string
    - Remove ALL '*' characters
    - Remove backticks
    - Strip whitespace and collapse repeated whitespace
    - Convert empty strings or placeholders to None
    """
    if val is None or val is False:
        return None

    # Handle pandas / numpy NaN
    try:
        if str(val).lower() == "nan":
            return None
    except Exception:
        pass

    val_str = str(val)
    # Remove all markdown asterisks and backticks
    val_str = val_str.replace("*", "").replace("`", "").strip()

    # Strip surrounding quotes
    if (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")):
        val_str = val_str[1:-1].strip()

    # Collapse internal whitespace
    val_str = re.sub(r"\s+", " ", val_str)

    if not val_str or val_str.lower() in PLACEHOLDERS:
        return None

    return val_str


def clean_string_value(val: Optional[str]) -> Optional[str]:
    """
    Alias to clean_value for backwards compatibility across imports.
    """
    return clean_value(val)


class ProductInfo(BaseModel):
    """
    Pydantic schema representing normalized product attributes extracted from product descriptions.
    """
    manufacturer_part_number: Optional[str] = Field(
        default=None,
        description="The actual manufacturer model or part number preserved as-is."
    )
    brand: Optional[str] = Field(
        default=None,
        description="The manufacturer or brand name of the product."
    )
    product_type: Optional[str] = Field(
        default=None,
        description="The core product category or type (e.g. Sanding Belt, Stikit Film Disc, Abrasive Disc)."
    )
    size: Optional[str] = Field(
        default=None,
        description="Normalized dimension string (e.g., '1/2 in x 18 in', '5 in', '2.75 in x 30 in')."
    )
    quantity: Optional[int] = Field(
        default=None,
        ge=1,
        description="Package item count. Must be >= 1 when present. Grit ratings (P80, P120) are NOT quantities."
    )
    understanding_status: Optional[str] = Field(
        default="failed",
        description="Processing status: 'success', 'partial', 'ambiguous', or 'failed'."
    )
    confidence: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 based on evidence quality."
    )

    @field_validator("manufacturer_part_number", "brand", "product_type", "size", mode="before")
    @classmethod
    def sanitize_strings(cls, value: Optional[str]) -> Optional[str]:
        return clean_string_value(value)
