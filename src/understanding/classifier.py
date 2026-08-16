import os
import re
import json
import logging
import pandas as pd
from typing import Optional, Dict, Tuple, List, Set, Any
from rapidfuzz import fuzz, process
import dotenv
from google import genai
from google.genai import types

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


def normalize_text_token(text: Optional[str]) -> str:
    if not text or not isinstance(text, str):
        return ""
    t = text.strip().lower()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


class TaxonomyClassifier:
    """
    Part B — Phase 4 Classification Engine (Quality-Improved)
    Deterministic-first product classification against data/master/product_taxonomy.csv.
    Includes RapidFuzz candidate generation, broad parent category fallback,
    and Gemini LLM candidate selector fallback.
    """

    def __init__(self, taxonomy_path: str = "data/master/product_taxonomy.csv", client: Optional[genai.Client] = None):
        self.taxonomy_path = taxonomy_path

        # Initialize Gemini Client if not provided
        if client is not None:
            self.client = client
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                try:
                    self.client = genai.Client(api_key=api_key)
                except Exception as e:
                    logger.warning(f"Could not initialize Gemini Client: {e}")
                    self.client = None
            else:
                self.client = None

        # Taxonomy data structures
        self.taxonomy_df: pd.DataFrame = None
        self.categories_by_id: Dict[str, dict] = {}
        self.source_ptype_to_cat_id: Dict[str, str] = {}
        self.norm_cat_name_to_cat_id: Dict[str, str] = {}

        # LLM performance metrics
        self.llm_stats = {
            "calls": 0,
            "accepted": 0,
            "rejected": 0,
            "null": 0
        }

        # Cache for repeated product classifications
        self.classification_cache: Dict[str, dict] = {}

        self._load_taxonomy()

    def _load_taxonomy(self):
        if not os.path.exists(self.taxonomy_path):
            raise FileNotFoundError(f"Taxonomy file '{self.taxonomy_path}' not found! Build taxonomy first.")

        self.taxonomy_df = pd.read_csv(self.taxonomy_path)

        for _, row in self.taxonomy_df.iterrows():
            c_id = str(row['category_id']).strip()
            c_name = str(row['category_name']).strip()
            p_id = str(row['parent_category_id']).strip() if pd.notna(row['parent_category_id']) else None
            p_name = str(row['parent_category_name']).strip() if pd.notna(row['parent_category_name']) else None
            level = int(row['hierarchy_level'])
            c_path = str(row['category_path']).strip()

            src_ptypes = [s.strip() for s in str(row['source_product_types']).split(';') if s.strip()] if pd.notna(row['source_product_types']) else []
            keywords = [k.strip() for k in str(row['keywords']).split(';') if k.strip()] if pd.notna(row['keywords']) else []
            aliases = [a.strip() for a in str(row['aliases']).split(';') if a.strip()] if pd.notna(row['aliases']) else []

            rec = {
                "category_id": c_id,
                "category_name": c_name,
                "parent_category_id": p_id,
                "parent_category_name": p_name,
                "hierarchy_level": level,
                "category_path": c_path,
                "source_product_types": src_ptypes,
                "keywords": keywords,
                "aliases": aliases
            }
            self.categories_by_id[c_id] = rec
            self.norm_cat_name_to_cat_id[normalize_text_token(c_name)] = c_id

            for pt in src_ptypes:
                norm_pt = normalize_text_token(pt)
                if norm_pt and norm_pt not in self.source_ptype_to_cat_id:
                    self.source_ptype_to_cat_id[norm_pt] = c_id

    def verify_lov(self, category_id: Optional[str]) -> Tuple[bool, Optional[dict]]:
        """
        LOV Verification Check:
        Verifies that category_id exists in product_taxonomy.csv, has valid name, parent, and path.
        """
        if not category_id or not isinstance(category_id, str):
            return False, None

        c_id = category_id.strip()
        if c_id not in self.categories_by_id:
            return False, None

        rec = self.categories_by_id[c_id]
        if not rec["category_name"] or not rec["category_path"]:
            return False, None

        return True, rec

    def classify_product(
        self,
        product_type: Optional[str] = None,
        part_desc: Optional[str] = None,
        brand: Optional[str] = None,
        manufacturer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classifies a product using Deterministic Rules -> RapidFuzz Candidate Generation -> Safe Broad Parent Fallback -> LLM Candidate Selector -> LOV Verification.
        """
        cache_key = f"{str(product_type).strip()}|{str(part_desc).strip()}|{str(brand).strip()}|{str(manufacturer).strip()}"
        if cache_key in self.classification_cache:
            return self.classification_cache[cache_key]

        pt_clean = str(product_type).strip() if product_type and pd.notna(product_type) else ""
        desc_clean = str(part_desc).strip() if part_desc and pd.notna(part_desc) else ""
        norm_pt = normalize_text_token(pt_clean)
        norm_desc = normalize_text_token(desc_clean)

        empty_res = {
            "category_id": None,
            "category_name": None,
            "parent_category_id": None,
            "parent_category_name": None,
            "hierarchy_level": None,
            "category_path": None,
            "classification_status": "unmatched",
            "classification_method": "unmatched",
            "classification_confidence": 0.0
        }

        if not pt_clean and not desc_clean:
            return empty_res

        raw_match_cat_id = None
        match_method = "unmatched"
        raw_confidence = 0.0

        # =========================================================================
        # Stage 1: Exact Product Type Match (rule_exact)
        # =========================================================================
        if norm_pt and norm_pt in self.source_ptype_to_cat_id:
            raw_match_cat_id = self.source_ptype_to_cat_id[norm_pt]
            match_method = "rule_exact"
            raw_confidence = 1.00

        # =========================================================================
        # Stage 2: Normalized Product Type Match (rule_normalized)
        # =========================================================================
        if not raw_match_cat_id and norm_pt:
            if norm_pt in self.norm_cat_name_to_cat_id:
                raw_match_cat_id = self.norm_cat_name_to_cat_id[norm_pt]
                match_method = "rule_normalized"
                raw_confidence = 0.95
            else:
                for src_pt, cat_id in self.source_ptype_to_cat_id.items():
                    if src_pt in norm_pt or norm_pt in src_pt:
                        raw_match_cat_id = cat_id
                        match_method = "rule_normalized"
                        ratio = len(src_pt) / max(len(norm_pt), len(src_pt), 1)
                        raw_confidence = round(0.90 + (0.05 * ratio), 2)
                        break

        # =========================================================================
        # Stage 3: Keyword & Alias Token Matching (rule_keyword)
        # =========================================================================
        if not raw_match_cat_id:
            search_text = f"{norm_pt} {norm_desc}".strip()
            best_cat_id = None
            best_score = 0.0

            # Prefer Level 3 leaf categories first
            for level_target in [3, 2, 1]:
                target_cats = [c for c in self.categories_by_id.values() if c["hierarchy_level"] == level_target]
                for cat in target_cats:
                    c_id = cat["category_id"]
                    score = 0.0

                    for kw in cat["keywords"]:
                        norm_kw = normalize_text_token(kw)
                        if norm_kw and norm_kw in search_text:
                            score += 2.5 if " " in norm_kw else 1.0

                    for alias in cat["aliases"]:
                        norm_alias = normalize_text_token(alias)
                        if norm_alias and norm_alias in search_text:
                            score += 3.0

                    for pt in cat["source_product_types"]:
                        norm_ptype = normalize_text_token(pt)
                        if norm_ptype and norm_ptype in search_text:
                            score += 3.5

                    if score > best_score:
                        best_score = score
                        best_cat_id = c_id

                if best_cat_id and best_score >= 2.0:
                    raw_match_cat_id = best_cat_id
                    match_method = "rule_keyword"
                    raw_confidence = round(min(0.85 + (best_score * 0.02), 0.94), 2)
                    break

        # =========================================================================
        # Stage 4: Enhanced Candidate Generation & Broad Parent Fallback (candidate_match)
        # =========================================================================
        if not raw_match_cat_id:
            candidates = self._get_candidates_for_product(norm_pt, norm_desc, brand=brand, manufacturer=manufacturer, top_n=5)

            if candidates:
                top_cat_id, top_cand_score = candidates[0]
                if top_cand_score >= 45.0:
                    raw_match_cat_id = top_cat_id
                    match_method = "candidate_match"
                    raw_confidence = round(min(0.75 + (top_cand_score / 200.0), 0.88), 2)

        # =========================================================================
        # Stage 5: Gemini LLM Candidate Selector Fallback (llm)
        # =========================================================================
        if not raw_match_cat_id and self.client is not None:
            candidates = self._get_candidates_for_product(norm_pt, norm_desc, brand=brand, manufacturer=manufacturer, top_n=5)
            if candidates:
                cand_ids = [c[0] for c in candidates]
                llm_cat_id, llm_conf = self._call_llm_candidate_selector(
                    desc_clean or pt_clean,
                    product_type=pt_clean,
                    brand=brand,
                    manufacturer=manufacturer,
                    candidate_ids=cand_ids
                )
                if llm_cat_id and llm_cat_id in cand_ids:
                    raw_match_cat_id = llm_cat_id
                    match_method = "llm"
                    raw_confidence = round(max(0.70, min(llm_conf, 0.85)), 2)

        # =========================================================================
        # MANDATORY LOV VERIFICATION & OUTPUT FORMATION
        # =========================================================================
        is_valid, rec = self.verify_lov(raw_match_cat_id)

        if not is_valid or rec is None:
            res = empty_res
        else:
            status_val = "classified" if raw_confidence >= 0.70 else "ambiguous"
            res = {
                "category_id": rec["category_id"],
                "category_name": rec["category_name"],
                "parent_category_id": rec["parent_category_id"],
                "parent_category_name": rec["parent_category_name"],
                "hierarchy_level": rec["hierarchy_level"],
                "category_path": rec["category_path"],
                "classification_status": status_val,
                "classification_method": match_method,
                "classification_confidence": float(raw_confidence)
            }

        self.classification_cache[cache_key] = res
        return res

    def _get_candidates_for_product(
        self,
        norm_pt: str,
        norm_desc: str,
        brand: Optional[str] = None,
        manufacturer: Optional[str] = None,
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Generates candidate taxonomy categories using RapidFuzz, token similarity,
        keywords, aliases, and brand/manufacturer context.
        Returns sorted list of (category_id, candidate_score).
        """
        search_text = f"{norm_pt} {norm_desc} {normalize_text_token(brand)} {normalize_text_token(manufacturer)}".strip()
        if not search_text:
            return []

        candidate_scores: Dict[str, float] = {}

        for cat in self.categories_by_id.values():
            c_id = cat["category_id"]
            c_name = cat["category_name"]
            c_path = cat["category_path"]

            # RapidFuzz similarity against category path and category name
            path_sim = float(fuzz.token_set_ratio(search_text, normalize_text_token(c_path)))
            name_sim = float(fuzz.token_set_ratio(search_text, normalize_text_token(c_name)))
            base_score = max(path_sim, name_sim)

            # Keyword and alias boost
            kw_boost = 0.0
            for kw in cat["keywords"]:
                norm_kw = normalize_text_token(kw)
                if norm_kw and norm_kw in search_text:
                    kw_boost += 15.0 if " " in norm_kw else 8.0

            for alias in cat["aliases"]:
                norm_alias = normalize_text_token(alias)
                if norm_alias and norm_alias in search_text:
                    kw_boost += 20.0

            for pt in cat["source_product_types"]:
                norm_ptype = normalize_text_token(pt)
                if norm_ptype and norm_ptype in search_text:
                    kw_boost += 25.0

            total_score = base_score + kw_boost

            # Filter out weak candidates (< 40 score)
            if total_score >= 40.0:
                candidate_scores[c_id] = total_score

        sorted_cands = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_cands[:top_n]

    def _call_llm_candidate_selector(
        self,
        product_desc: str,
        product_type: str = "",
        brand: Optional[str] = None,
        manufacturer: Optional[str] = None,
        candidate_ids: List[str] = None
    ) -> Tuple[Optional[str], float]:
        """
        LLM Candidate Selector Fallback.
        STRICT REQUIREMENT: Returns ONLY a valid category_id from candidate_ids or null.
        Prompt explicitly says LLM cannot create or invent categories.
        """
        if not self.client or not candidate_ids:
            return None, 0.0

        if getattr(self, "llm_disabled", False):
            return None, 0.0

        candidates_info = []
        for c_id in candidate_ids:
            if c_id in self.categories_by_id:
                rec = self.categories_by_id[c_id]
                candidates_info.append(f"- ID: {rec['category_id']} | Name: {rec['category_name']} | Path: {rec['category_path']}")

        prompt = f"""You are selecting a category from an approved controlled taxonomy.
Product Description: "{product_desc}"
Product Type: "{product_type}"
Brand: "{brand or ''}"
Manufacturer: "{manufacturer or ''}"

Allowed Candidate List:
{chr(10).join(candidates_info)}

Instructions:
You are NOT allowed to create, rename, modify, or invent a category.
Return exactly one category_id from the provided candidates in valid JSON format:
{{"category_id": "<SELECTED_ID>", "confidence": 0.75}}

If none are semantically appropriate, return {{"category_id": null, "confidence": 0.0}}.
"""
        try:
            self.llm_stats["calls"] += 1
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            if response and response.text:
                parsed = json.loads(response.text)
                res_id = parsed.get("category_id")
                res_conf = float(parsed.get("confidence", 0.75))

                if res_id is None or str(res_id).strip().lower() in ["null", "none", ""]:
                    self.llm_stats["null"] += 1
                    return None, 0.0

                if res_id in candidate_ids and res_id in self.categories_by_id:
                    self.llm_stats["accepted"] += 1
                    return res_id, res_conf
                else:
                    self.llm_stats["rejected"] += 1
                    return None, 0.0
        except Exception as e:
            err_msg = str(e)
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                logger.warning("LLM API daily quota exhausted. Disabling further LLM calls for this session.")
                self.llm_disabled = True
            else:
                logger.warning(f"LLM candidate selector call failed: {e}")
            self.llm_stats["rejected"] += 1

        return None, 0.0
