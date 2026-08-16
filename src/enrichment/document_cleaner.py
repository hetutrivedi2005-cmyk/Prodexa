import re
from typing import Dict, List, Any


class DocumentCleaner:
    """
    Component 5 (Phase 8.1 Enhanced): Document Cleaner Engine.
    Cleans document text artifacts (repeated headers, footers, broken line wraps, excessive whitespace)
    without modifying technical numbers, fractions, or measurement units.
    """

    def clean_segment_text(self, text: str) -> str:
        if not text:
            return ""

        lines = [line.strip() for line in text.split("\n")]
        cleaned_lines = []

        for line in lines:
            if not line:
                continue
            # Remove header/footer noise
            if re.match(r"^Page \d+ of \d+$", line, re.IGNORECASE):
                continue
            if re.match(r"^Confidential - For Internal Use Only$", line, re.IGNORECASE):
                continue
            cleaned = re.sub(r"[ \t]+", " ", line).strip()
            cleaned_lines.append(cleaned)

        return "\n".join(cleaned_lines)

    def clean_segments(self, segments: List[dict]) -> List[dict]:
        cleaned_segments = []
        for seg in segments:
            c_text = self.clean_segment_text(seg.get("text", ""))
            if c_text:
                new_seg = dict(seg)
                new_seg["text"] = c_text
                cleaned_segments.append(new_seg)
        return cleaned_segments
