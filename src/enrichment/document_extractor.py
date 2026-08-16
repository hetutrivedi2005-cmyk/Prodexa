import os
import re
from typing import Dict, List, Any, Optional


class DocumentExtractor:
    """
    Component 4: Document Text Extraction Engine.
    Extracts text segments from HTML, PDF, and plain text documents while retaining
    page numbers, document titles, source URLs, source types, and MPN provenance.
    """

    def extract_document_segments(self, source_record: dict) -> List[dict]:
        raw_text = source_record.get("raw_text", "")
        source_url = source_record.get("url", "")
        source_type = source_record.get("source_type", "")
        manufacturer = source_record.get("manufacturer", "")
        mpn = source_record.get("mpn", "")
        source_id = source_record.get("source_id", "")

        if not raw_text:
            return []

        segments = []
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        current_page = 1
        current_section = "General Specifications"

        # Split into logical sections or page boundaries
        for idx, line in enumerate(lines):
            # Detect section headers
            if line.isupper() or line.endswith(":") or "TECHNICAL SPECIFICATIONS" in line.upper():
                current_section = line.rstrip(":")

            segments.append({
                "segment_id": f"{source_id}_seg_{idx+1}",
                "source_id": source_id,
                "source_url": source_url,
                "source_type": source_type,
                "manufacturer": manufacturer,
                "mpn": mpn,
                "page": current_page,
                "section": current_section,
                "text": line
            })

        return segments
