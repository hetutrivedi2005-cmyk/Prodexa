import re
import logging
from typing import Optional, Dict, Tuple, List
from rapidfuzz import fuzz, process
from google import genai
from google.genai import types

from src.understanding.master_data import MasterDataLoader

logger = logging.getLogger(__name__)


def normalize_name(value: Optional[str]) -> str:
    """
    Reusable name normalization function.
    - Convert to string, lowercase, trim spaces
    - Remove surrounding punctuation
    - Normalize repeated whitespace & common punctuation
    - Remove parenthesized codes when appropriate (e.g. 'Freud Inc (2435)' -> 'freud inc')
    """
    if value is None or not isinstance(value, str):
        return ""

    val = str(value).strip().lower()
    if not val:
        return ""

    # Remove code in parentheses at the end of string, e.g. (2435), (JAMIN), (MIRUS)
    val = re.sub(r"\s*\([^)]*\)\s*$", "", val).strip()

    # Normalize punctuation spacing
    val = re.sub(r"[,\.-]+", " ", val)

    # Normalize whitespace
    val = re.sub(r"\s+", " ", val).strip()

    return val


class EntityResolver:
    """
    Phase 3 Entity Resolution Engine for Manufacturer & Brand Matching.
    Enforces Deterministic First Matching -> RapidFuzz -> Ambiguity Check -> LLM Candidate Selection.
    """

    def __init__(self, master_loader: Optional[MasterDataLoader] = None, client: Optional[genai.Client] = None):
        self.loader = master_loader or MasterDataLoader()
        self.client = client

    def resolve_manufacturer(
        self,
        raw_manuf: Optional[str],
        product_desc: Optional[str] = None
    ) -> Dict[str, Optional[object]]:
        """
        Resolves raw manufacturer input against Manufacturer Reference Data.
        Returns dict with:
            - manufacturer_canonical
            - manufacturer_id
            - manufacturer_match_status ('matched', 'ambiguous', 'unmatched')
            - manufacturer_match_method ('exact', 'normalized', 'fuzzy', 'llm', 'none')
            - manufacturer_confidence (float 0.0 to 1.0)
        """
        result = {
            "manufacturer_canonical": None,
            "manufacturer_id": None,
            "manufacturer_match_status": "unmatched",
            "manufacturer_match_method": "none",
            "manufacturer_confidence": 0.0
        }

        if not raw_manuf or str(raw_manuf).strip() in ["", "-", "nan", "none", "null"]:
            return result

        raw_str = str(raw_manuf).strip()
        norm_input = normalize_name(raw_str)

        if not norm_input:
            return result

        # ----------------------------------------------------
        # Stage 1: Exact Match
        # ----------------------------------------------------
        # Compare raw string directly against canonical names
        for canonical_name, rec in self.loader.manufacturer_records.items():
            if raw_str.lower() == canonical_name.lower():
                result.update({
                    "manufacturer_canonical": canonical_name,
                    "manufacturer_id": rec["reference_id"] or None,
                    "manufacturer_match_status": "matched",
                    "manufacturer_match_method": "exact",
                    "manufacturer_confidence": 1.0
                })
                return result

        # ----------------------------------------------------
        # Stage 2: Normalized Match
        # ----------------------------------------------------
        canonical_match = self.loader.normalized_manuf_lookup.get(norm_input)

        # Check by reference code if present (e.g. '2435', 'JAMIN', 'MIRUS')
        if not canonical_match:
            code_match = re.search(r"\(([^)]+)\)$", raw_str)
            if code_match:
                ref_code = code_match.group(1).strip().lower()
                canonical_match = self.loader.manuf_id_lookup.get(ref_code)

        if canonical_match:
            rec = self.loader.manufacturer_records[canonical_match]
            result.update({
                "manufacturer_canonical": canonical_match,
                "manufacturer_id": rec["reference_id"] or None,
                "manufacturer_match_status": "matched",
                "manufacturer_match_method": "normalized",
                "manufacturer_confidence": 0.95
            })
            return result

        # ----------------------------------------------------
        # Stage 3: RapidFuzz Match & Candidate Ranking
        # ----------------------------------------------------
        choices = list(self.loader.manufacturer_records.keys())
        norm_choices = [normalize_name(c) for c in choices]

        # Extract top 2 fuzzy matches
        fuzzy_results = process.extract(
            norm_input,
            norm_choices,
            scorer=fuzz.token_sort_ratio,
            limit=2
        )

        if not fuzzy_results:
            return result

        top1_name = choices[fuzzy_results[0][2]]
        top1_score = float(fuzzy_results[0][1])

        top2_name = choices[fuzzy_results[1][2]] if len(fuzzy_results) > 1 else None
        top2_score = float(fuzzy_results[1][1]) if len(fuzzy_results) > 1 else 0.0

        # Ambiguity Check: If top 2 candidates are too close (e.g. 91.2 vs 90.8)
        is_ambiguous = (
            top1_score >= 90.0 and
            top2_score >= 90.0 and
            (top1_score - top2_score) < 2.0
        )

        if is_ambiguous:
            # Stage 4: LLM Fallback (Constrained to candidate list)
            if self.client is not None:
                llm_choice = self._call_llm_for_manufacturer(raw_str, [top1_name, top2_name])
                if llm_choice and llm_choice in self.loader.manufacturer_records:
                    rec = self.loader.manufacturer_records[llm_choice]
                    result.update({
                        "manufacturer_canonical": llm_choice,
                        "manufacturer_id": rec["reference_id"] or None,
                        "manufacturer_match_status": "matched",
                        "manufacturer_match_method": "llm",
                        "manufacturer_confidence": 0.90
                    })
                    return result

            # If LLM unavailable or returns ambiguous
            rec1 = self.loader.manufacturer_records[top1_name]
            result.update({
                "manufacturer_canonical": top1_name,
                "manufacturer_id": rec1["reference_id"] or None,
                "manufacturer_match_status": "ambiguous",
                "manufacturer_match_method": "fuzzy",
                "manufacturer_confidence": round(top1_score / 100.0, 2)
            })
            return result

        # Single Strong or Acceptable Fuzzy Match
        if top1_score >= 90.0:
            rec = self.loader.manufacturer_records[top1_name]
            result.update({
                "manufacturer_canonical": top1_name,
                "manufacturer_id": rec["reference_id"] or None,
                "manufacturer_match_status": "matched",
                "manufacturer_match_method": "fuzzy",
                "manufacturer_confidence": round(top1_score / 100.0, 2)
            })
            return result

        return result

    def _call_llm_for_manufacturer(self, raw_input: str, candidates: List[str]) -> str:
        """
        LLM Fallback for Manufacturer Resolution.
        STRICT REQUIREMENT: Must ONLY select from candidates or return 'ambiguous'.
        Never invents new names.
        """
        if not self.client or not candidates:
            return "ambiguous"

        prompt = f"""You are a master catalog entity resolver.
Raw Manufacturer Input: "{raw_input}"
Allowed Candidate List:
{chr(10).join([f'- {c}' for c in candidates])}

Instructions:
Select the exact candidate from the list that best matches the raw manufacturer input.
If none match cleanly or if it is ambiguous, respond ONLY with "ambiguous".
DO NOT create or invent any new manufacturer name outside the candidate list.

Return ONLY the exact string from the candidate list or "ambiguous".
"""
        try:
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            res_text = response.text.strip() if response and response.text else "ambiguous"
            for cand in candidates:
                if res_text.lower() == cand.lower():
                    return cand
        except Exception as e:
            logger.warning(f"LLM fallback failed: {e}")

        return "ambiguous"

    def resolve_brand(
        self,
        raw_brand: Optional[str],
        phase2_brand: Optional[str],
        resolved_manufacturer: Optional[str] = None
    ) -> Dict[str, Optional[object]]:
        """
        Resolves brand input against Brand Reference Data & Manufacturer-Brand Relationships.
        Returns dict with:
            - brand_canonical
            - brand_id (Internal BRD_* ID)
            - brand_match_status ('matched', 'ambiguous', 'unmatched')
            - brand_match_method ('exact', 'normalized', 'fuzzy', 'llm', 'none')
            - brand_confidence (float 0.0 to 1.0)
        """
        result = {
            "brand_canonical": None,
            "brand_id": None,
            "brand_match_status": "unmatched",
            "brand_match_method": "none",
            "brand_confidence": 0.0
        }

        # Select best candidate brand signal (Priority: Phase 2 Brand -> Raw Brand)
        candidate_input = phase2_brand or raw_brand
        if not candidate_input or str(candidate_input).strip() in ["", "-", "nan", "none", "null"]:
            # If brand missing, attempt manufacturer relationship lookup
            if resolved_manufacturer and resolved_manufacturer in self.loader.manuf_to_brands:
                known_brands = list(self.loader.manuf_to_brands[resolved_manufacturer])
                if len(known_brands) == 1:
                    b_canonical = known_brands[0]
                    rec = self.loader.brand_records[b_canonical]
                    result.update({
                        "brand_canonical": b_canonical,
                        "brand_id": rec["brand_id"],
                        "brand_match_status": "matched",
                        "brand_match_method": "normalized",
                        "brand_confidence": 0.90
                    })
                    return result
            return result

        raw_b_str = str(candidate_input).strip()
        norm_b = normalize_name(raw_b_str)

        # ----------------------------------------------------
        # Stage 1: Exact Brand Match
        # ----------------------------------------------------
        for canonical_b, rec in self.loader.brand_records.items():
            if raw_b_str.lower() == canonical_b.lower():
                result.update({
                    "brand_canonical": canonical_b,
                    "brand_id": rec["brand_id"],
                    "brand_match_status": "matched",
                    "brand_match_method": "exact",
                    "brand_confidence": 1.0
                })
                break

        # ----------------------------------------------------
        # Stage 2: Normalized Brand Match
        # ----------------------------------------------------
        if not result["brand_canonical"]:
            canonical_b = self.loader.normalized_brand_lookup.get(norm_b)
            if canonical_b:
                rec = self.loader.brand_records[canonical_b]
                result.update({
                    "brand_canonical": canonical_b,
                    "brand_id": rec["brand_id"],
                    "brand_match_status": "matched",
                    "brand_match_method": "normalized",
                    "brand_confidence": 0.95
                })

        # ----------------------------------------------------
        # Stage 3: Fuzzy Brand Match
        # ----------------------------------------------------
        if not result["brand_canonical"]:
            choices = list(self.loader.brand_records.keys())
            norm_choices = [normalize_name(c) for c in choices]

            fuzzy_res = process.extract(norm_b, norm_choices, scorer=fuzz.token_sort_ratio, limit=2)
            if fuzzy_res:
                top1_b = choices[fuzzy_res[0][2]]
                top1_score = float(fuzzy_res[0][1])

                if top1_score >= 90.0:
                    rec = self.loader.brand_records[top1_b]
                    result.update({
                        "brand_canonical": top1_b,
                        "brand_id": rec["brand_id"],
                        "brand_match_status": "matched",
                        "brand_match_method": "fuzzy",
                        "brand_confidence": round(top1_score / 100.0, 2)
                    })

        # ----------------------------------------------------
        # Stage 4: Relationship Validation Check
        # ----------------------------------------------------
        res_b = result["brand_canonical"]
        if res_b and resolved_manufacturer:
            # Validate relationship against derived reference data
            is_valid_rel = self.loader.validate_relationship(resolved_manufacturer, res_b)
            if not is_valid_rel:
                # If brand is matched independently but has unverified manufacturer relationship
                # Keep resolved brand but adjust status if manufacturer is present
                known_manuf_brands = self.loader.manuf_to_brands.get(resolved_manufacturer, set())
                if known_manuf_brands and res_b not in known_manuf_brands:
                    result["brand_match_status"] = "ambiguous"

        return result
