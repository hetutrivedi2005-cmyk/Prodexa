import os
import json
import re
from typing import Dict, List, Any


class DocumentChunker:
    """
    Component 6 (Phase 8.1 Enhanced): Document Chunker Engine.
    Splits cleaned text segments into attribute-aware sections (SPECIFICATIONS, DIMENSIONS,
    MATERIAL, ELECTRICAL, PACKAGING, TECHNICAL DATA) while retaining mandatory chunk provenance metadata.
    """

    TARGET_SECTIONS = [
        "TECHNICAL SPECIFICATIONS", "PRODUCT OVERVIEW", "SPECIFICATIONS",
        "DIMENSIONS", "MATERIAL", "ELECTRICAL", "COMPATIBILITY",
        "PACKAGING", "TECHNICAL DATA"
    ]

    def chunk_segments(self, segments: List[dict]) -> List[dict]:
        if not segments:
            return []

        chunks = []
        grouped: Dict[tuple, List[str]] = {}
        seg_meta: Dict[tuple, dict] = {}

        for seg in segments:
            section_name = seg.get("section", "TECHNICAL SPECIFICATIONS").upper()
            normalized_section = section_name
            for ts in self.TARGET_SECTIONS:
                if ts in section_name:
                    normalized_section = ts
                    break

            key = (seg["source_id"], normalized_section, seg["page"])
            if key not in grouped:
                grouped[key] = []
                seg_meta[key] = {
                    "source_id": seg["source_id"],
                    "source_url": seg["source_url"],
                    "source_type": seg["source_type"],
                    "manufacturer": seg["manufacturer"],
                    "mpn": seg["mpn"],
                    "normalized_mpn": re.sub(r"[^A-Z0-9]", "", str(seg["mpn"]).upper()),
                    "page": seg["page"],
                    "section": normalized_section
                }
            grouped[key].append(seg["text"])

        chunk_idx = 1
        for key, text_lines in grouped.items():
            meta = seg_meta[key]
            combined_text = "\n".join(text_lines)

            chunks.append({
                "chunk_id": f"CHUNK-{meta['source_id']}-{chunk_idx:04d}",
                "source_id": meta["source_id"],
                "source_url": meta["source_url"],
                "source_type": meta["source_type"],
                "manufacturer": meta["manufacturer"],
                "mpn": meta["mpn"],
                "normalized_mpn": meta["normalized_mpn"],
                "page": meta["page"],
                "section": meta["section"],
                "text": combined_text
            })
            chunk_idx += 1

        return chunks

    def save_chunks_jsonl(self, chunks: List[dict], output_path: str = "data/enrichment/document_chunks.jsonl"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c) + "\n")
