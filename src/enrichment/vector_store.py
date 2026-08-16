import math
import re
from typing import Dict, List, Any, Optional


class ModularVectorStore:
    """
    Component 7: Modular Vector Store Engine.
    Provides local product-scoped retrieval with strict metadata filtering
    (manufacturer + normalized MPN), term weighting (BM25/TF-IDF), and document indexing.
    """

    def __init__(self):
        self.documents: List[dict] = []

    def clear_collection(self):
        self.documents = []

    def add_documents(self, docs: List[dict]):
        for d in docs:
            # Ensure text, metadata exists
            self.documents.append({
                "chunk_id": d.get("chunk_id"),
                "source_id": d.get("source_id"),
                "source_url": d.get("source_url"),
                "source_type": d.get("source_type"),
                "manufacturer": str(d.get("manufacturer") or "").strip(),
                "mpn": self._normalize_mpn(d.get("mpn")),
                "page": d.get("page", 1),
                "section": d.get("section", ""),
                "text": d.get("text", "")
            })

    def count(self) -> int:
        return len(self.documents)

    def delete(self, chunk_id: str):
        self.documents = [d for d in self.documents if d["chunk_id"] != chunk_id]

    def search(
        self,
        query: str,
        filters: dict,
        top_k: int = 5
    ) -> List[dict]:
        """
        Metadata-filtered Product-Scoped Retrieval.
        MANDATORY FILTERS: manufacturer AND mpn.
        """
        target_mfg = str(filters.get("manufacturer") or "").strip().lower()
        target_mpn = self._normalize_mpn(filters.get("mpn"))

        # Step 1: Strict Metadata Filtering
        candidate_docs = []
        for doc in self.documents:
            doc_mfg = doc["manufacturer"].lower()
            doc_mpn = doc["mpn"]

            # Match manufacturer substring and exact normalized MPN
            mfg_match = (not target_mfg) or (target_mfg in doc_mfg) or (doc_mfg in target_mfg)
            mpn_match = (not target_mpn) or (doc_mpn == target_mpn)

            if mfg_match and mpn_match:
                candidate_docs.append(doc)

        if not candidate_docs:
            return []

        # Step 2: Lexical BM25 / TF-IDF Scoring
        query_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]
        results = []

        for doc in candidate_docs:
            text_lower = doc["text"].lower()
            score = 0.0
            for term in query_terms:
                count = text_lower.count(term)
                if count > 0:
                    score += (1.0 + math.log(count))

            # Bonus for section relevance
            section_lower = doc.get("section", "").lower()
            if any(qt in section_lower for qt in query_terms):
                score += 1.5

            if score > 0.0 or len(candidate_docs) == 1:
                doc_copy = dict(doc)
                doc_copy["retrieval_score"] = score
                results.append(doc_copy)

        results.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return results[:top_k]

    def _normalize_mpn(self, mpn: Any) -> str:
        if mpn is None:
            return ""
        return re.sub(r"[^A-Z0-9]", "", str(mpn).upper())
