import csv
import io
import re
from typing import List, Dict, Any, Tuple

class CSVAdapter:
    """
    Intelligent Input Adapter & Column Understanding Engine for Unstructured CSV Feeds.
    Normalizes arbitrary CSV headers and data rows into Canonical Product Records.
    """

    # Keyword patterns for heuristic column detection
    PRODUCT_ID_PATTERNS = [
        r"product[_\s]*id", r"prod[_\s]*id", r"item[_\s]*id", r"^id$", r"product[_\s]*code"
    ]
    PRODUCT_PATTERNS = [
        r"product[_\s]*name", r"item[_\s]*description", r"product[_\s]*description",
        r"product[_\s]*title", r"item[_\s]*name", r"description", r"product", r"item",
        r"title", r"details", r"part[_\s]*description", r"goods", r"article"
    ]
    BRAND_PATTERNS = [
        r"brand", r"brand[_\s]*name", r"company", r"vendor", r"make", r"trade[_\s]*mark", r"label"
    ]
    MANUFACTURER_PATTERNS = [
        r"manufacturer", r"manufacturer[_\s]*name", r"mfr", r"maker", r"mfg", r"producer"
    ]
    MPN_PATTERNS = [
        r"mpn", r"sku", r"part[_\s]*number", r"part[_\s]*no", r"item[_\s]*no",
        r"model", r"model[_\s]*number", r"part#", r"catalog[_\s]*number", r"identifier"
    ]
    CATEGORY_PATTERNS = [
        r"category", r"product[_\s]*type", r"segment", r"group", r"classification", r"dept", r"department", r"type"
    ]
    UPC_PATTERNS = [
        r"upc", r"gtin", r"ean", r"barcode"
    ]

    @classmethod
    def parse_csv_bytes(cls, content: bytes) -> Tuple[List[str], List[Dict[str, str]]]:
        """
        Safely decodes and parses raw CSV content using fallback encodings.
        Returns raw header list and raw row dicts.
        """
        text = None
        for enc in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
            try:
                text = content.decode(enc)
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            text = content.decode("utf-8", errors="replace")

        # Detect delimiter if needed
        sample = text[:4096]
        delimiter = ","
        if ";" in sample and sample.count(";") > sample.count(","):
            delimiter = ";"
        elif "\t" in sample and sample.count("\t") > sample.count(","):
            delimiter = "\t"

        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return [], []

        raw_headers = [c.strip() for c in rows[0]]
        raw_data = []
        for row_idx, row in enumerate(rows[1:], start=1):
            if not any(c.strip() for c in row):  # Skip empty rows
                continue
            row_dict = {}
            for col_idx, header in enumerate(raw_headers):
                val = row[col_idx].strip() if col_idx < len(row) else ""
                row_dict[header] = val
            row_dict["_source_row_id"] = row_idx
            raw_data.append(row_dict)

        return raw_headers, raw_data

    @classmethod
    def detect_column_mapping(cls, raw_headers: List[str]) -> Dict[str, str]:
        """
        Maps raw CSV column headers to canonical field names:
        'product_id', 'product_name', 'brand', 'manufacturer', 'mpn', 'category', 'upc'
        """
        mapping = {}
        matched_canonical = set()

        def match_header(headers: List[str], patterns: List[str], canonical_field: str):
            if canonical_field in matched_canonical:
                return
            for h in headers:
                norm_h = h.lower().strip()
                for pat in patterns:
                    if re.search(rf"\b{pat}\b", norm_h) or norm_h == pat:
                        mapping[h] = canonical_field
                        matched_canonical.add(canonical_field)
                        return

        # Priority order matching
        match_header(raw_headers, cls.PRODUCT_ID_PATTERNS, "product_id")
        match_header(raw_headers, cls.MPN_PATTERNS, "mpn")
        match_header(raw_headers, cls.BRAND_PATTERNS, "brand")
        match_header(raw_headers, cls.MANUFACTURER_PATTERNS, "manufacturer")
        match_header(raw_headers, cls.CATEGORY_PATTERNS, "category")
        match_header(raw_headers, cls.PRODUCT_PATTERNS, "product_name")
        match_header(raw_headers, cls.UPC_PATTERNS, "upc")

        # Fallback: If product_name not matched, assign first unmapped column
        if "product_name" not in matched_canonical:
            for h in raw_headers:
                if h not in mapping:
                    mapping[h] = "product_name"
                    matched_canonical.add("product_name")
                    break

        return mapping

    @classmethod
    def create_canonical_records(cls, raw_data: List[Dict[str, str]], column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Converts raw CSV data rows into canonical internal product records.
        Preserves original _source_row_id and source_fields dict.
        """
        canonical_records = []
        for row in raw_data:
            source_row_id = row.get("_source_row_id", 1)
            raw_fields = {k: v for k, v in row.items() if k != "_source_row_id"}

            product_id = ""
            product_name = ""
            brand = ""
            manufacturer = ""
            mpn = ""
            category = ""
            upc = ""

            for raw_col, val in raw_fields.items():
                canon = column_mapping.get(raw_col)
                if canon == "product_id" and not product_id:
                    product_id = val
                elif canon == "product_name" and not product_name:
                    product_name = val
                elif canon == "brand" and not brand:
                    brand = val
                elif canon == "manufacturer" and not manufacturer:
                    manufacturer = val
                elif canon == "mpn" and not mpn:
                    mpn = val
                elif canon == "category" and not category:
                    category = val
                elif canon == "upc" and not upc:
                    upc = val

            # Fallback if product_name remains empty
            if not product_name:
                for v in raw_fields.values():
                    if v:
                        product_name = v
                        break

            record = {
                "source_row_id": source_row_id,
                "explicit_product_id": product_id if product_id else None,
                "product_name": product_name or f"Product #{source_row_id}",
                "raw_product_name": product_name,
                "brand": brand,
                "manufacturer": manufacturer,
                "mpn": mpn or f"MPN-{source_row_id:04d}",
                "category": category,
                "upc": upc,
                "source_fields": raw_fields
            }
            canonical_records.append(record)

        return canonical_records
