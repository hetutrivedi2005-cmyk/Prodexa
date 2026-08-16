import re
from typing import Dict, List, Any
from src.enrichment.vector_store import ModularVectorStore


class ProductRAGRetriever:
    """
    Component 8 (Phase 8.1 Enhanced): Product-Scoped RAG Retriever Engine.
    Generates deterministic attribute synonym query expansions, enforces strict
    product-scoped metadata filtering (manufacturer + normalized MPN), and calculates
    evidence scores.
    """

    ATTRIBUTE_SYNONYMS = {
        "dimensions": ["dimensions", "size", "measurements", "length", "width", "height", "belt dimensions"],
        "belt_dimensions": ["dimensions", "size", "measurements", "length", "width", "height", "belt dimensions"],
        "material": ["material", "abrasive material", "construction", "grain", "made of", "aluminum oxide", "ceramic", "steel"],
        "abrasive_type": ["material", "abrasive material", "grain", "abrasive type", "aluminum oxide", "ceramic"],
        "grit": ["grit", "grit rating", "grit size", "p80", "p120", "p150", "p180", "p220", "p320"],
        "pack_quantity": ["quantity", "pack", "package", "pieces", "pcs", "box", "pack quantity"],
        "quantity": ["quantity", "pack", "package", "pieces", "pcs", "box"],
        "voltage": ["voltage", "volts", "v", "operating voltage"],
        "wattage": ["wattage", "watts", "w", "power"],
        "arbor_size": ["arbor", "arbor size", "hole", "bore", "arbor hole"],
        "diameter": ["diameter", "disc diameter", "outer diameter", "size"]
    }

    def __init__(self, vector_store: ModularVectorStore):
        self.vector_store = vector_store

    def retrieve_evidence_for_missing_attributes(
        self,
        mpn: str,
        manufacturer: str,
        category_id: str,
        missing_attributes: List[str]
    ) -> Dict[str, List[dict]]:
        evidence_by_attribute: Dict[str, List[dict]] = {}

        if not missing_attributes or not mpn:
            return evidence_by_attribute

        norm_mpn = re.sub(r"[^A-Z0-9]", "", str(mpn).upper())

        for attr in missing_attributes:
            synonyms = self.ATTRIBUTE_SYNONYMS.get(attr, [attr])
            queries = [f"{mpn} {syn}" for syn in synonyms[:4]]
            queries.append(f"{mpn} specifications")

            attr_chunks = []
            seen_chunk_ids = set()

            for q in queries:
                results = self.vector_store.search(
                    query=q,
                    filters={
                        "manufacturer": manufacturer,
                        "mpn": mpn
                    },
                    top_k=5
                )

                for chunk in results:
                    cid = chunk["chunk_id"]
                    if cid in seen_chunk_ids:
                        continue

                    # Calculate Deterministic Evidence Score
                    score = self._calculate_evidence_score(chunk, norm_mpn, attr, synonyms)
                    if score >= 0.50:
                        seen_chunk_ids.add(cid)
                        chunk_copy = dict(chunk)
                        chunk_copy["retrieval_method"] = "lexical_product_scoped_retrieval"
                        chunk_copy["evidence_score"] = round(score, 2)
                        attr_chunks.append(chunk_copy)

            # Sort chunks by evidence_score descending
            attr_chunks.sort(key=lambda x: x.get("evidence_score", 0.0), reverse=True)
            evidence_by_attribute[attr] = attr_chunks

        return evidence_by_attribute

    def _calculate_evidence_score(
        self,
        chunk: dict,
        target_norm_mpn: str,
        attribute_name: str,
        synonyms: List[str]
    ) -> float:
        score = 0.0
        text = chunk.get("text", "")
        text_lower = text.lower()
        chunk_mpn = chunk.get("mpn", "")
        norm_chunk_mpn = re.sub(r"[^A-Z0-9]", "", str(chunk_mpn).upper())
        stype = chunk.get("source_type", "")
        section = chunk.get("section", "").upper()

        # 1. Exact MPN in chunk text: +0.30
        if target_norm_mpn and target_norm_mpn in text_lower.replace("-", "").replace(" ", ""):
            score += 0.30
        elif norm_chunk_mpn == target_norm_mpn:
            score += 0.30

        # 2. Attribute keyword match: +0.20
        if any(syn.lower() in text_lower for syn in synonyms):
            score += 0.20

        # 3. Official manufacturer source: +0.25
        if "manufacturer" in stype:
            score += 0.25
        elif "distributor" in stype:
            score += 0.15

        # 4. Technical PDF / datasheet: +0.15
        if "pdf" in stype or "datasheet" in stype:
            score += 0.15
        elif "product_page" in stype:
            score += 0.10

        # 5. Relevant section: +0.10
        if any(sec_kw in section for sec_kw in ["SPECIFICATIONS", "DIMENSIONS", "MATERIAL", "ELECTRICAL", "PACKAGING", "TECHNICAL"]):
            score += 0.10

        return max(0.0, min(1.0, score))
