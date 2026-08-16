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


def ground_text_in_source(val: str, source_fields: List[Any]) -> bool:
    if val is None or not str(val).strip():
        return False

    val_str = str(val).strip().lower()

    for field in source_fields:
        if field is None or pd.isna(field):
            continue
        f_str = str(field).strip().lower()
        if not f_str:
            continue
        if val_str in f_str:
            return True

    return False


class LOVResolver:
    """
    Part 2 — Controlled LOV Resolver Engine
    Implements strict resolution priority: exact -> normalized -> alias -> unit_normalization -> numeric_normalization -> type_aware_fuzzy -> llm_fallback -> unresolved.
    """

    def __init__(
        self,
        lov_csv_path: str = "data/master/attribute_lov.csv",
        uom_csv_path: str = "data/master/uom_master.csv",
        cat_attrs_csv_path: str = "data/master/category_attributes.csv",
        client: Optional[genai.Client] = None
    ):
        self.lov_csv_path = lov_csv_path
        self.uom_csv_path = uom_csv_path
        self.cat_attrs_csv_path = cat_attrs_csv_path

        if client is not None:
            self.client = client
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                try:
                    self.client = genai.Client(api_key=api_key)
                except Exception:
                    self.client = None
            else:
                self.client = None

        self.llm_stats = {"calls": 0, "accepted": 0, "rejected": 0}
        self.resolution_cache: Dict[str, dict] = {}

        self.lov_entries: List[dict] = []
        self.uom_map: Dict[str, str] = {}  # alias_lower -> canonical_uom
        self.category_allowed_attrs: Dict[str, Set[str]] = {}  # category_id -> set of allowed attribute_names

        self._load_masters()

    def _load_masters(self):
        # Load Category Attributes Master
        if os.path.exists(self.cat_attrs_csv_path):
            df_ca = pd.read_csv(self.cat_attrs_csv_path)
            for _, r in df_ca.iterrows():
                cid = str(r['category_id']).strip()
                aid = str(r['attribute_id']).strip()
                if cid not in self.category_allowed_attrs:
                    self.category_allowed_attrs[cid] = set()
                self.category_allowed_attrs[cid].add(aid)

        # Load UOM Master
        if os.path.exists(self.uom_csv_path):
            df_u = pd.read_csv(self.uom_csv_path)
            for _, r in df_u.iterrows():
                c_uom = str(r['canonical_uom']).strip()
                n_uom = str(r['normalized_uom']).strip().lower()
                self.uom_map[n_uom] = c_uom
                if pd.notna(r['aliases']):
                    for a in str(r['aliases']).split(';'):
                        if a.strip():
                            self.uom_map[a.strip().lower()] = c_uom

        # Load Attribute LOV Master
        if os.path.exists(self.lov_csv_path):
            df_l = pd.read_csv(self.lov_csv_path)
            for _, r in df_l.iterrows():
                entry = {
                    "lov_id": str(r['attribute_lov_id']).strip(),
                    "attribute_name": str(r['attribute_name']).strip(),
                    "attribute_type": str(r['attribute_type']).strip(),
                    "canonical_value": str(r['canonical_value']).strip(),
                    "normalized_value": str(r['normalized_value']).strip().lower(),
                    "aliases": [a.strip().lower() for a in str(r['aliases']).split(';') if a.strip()] if pd.notna(r['aliases']) else [],
                    "unit": str(r['unit']).strip() if pd.notna(r['unit']) else "",
                    "allowed_category_ids": [c.strip() for c in str(r['allowed_category_ids']).split(';') if c.strip()] if pd.notna(r['allowed_category_ids']) else []
                }
                self.lov_entries.append(entry)

    def resolve_value(
        self,
        category_id: Optional[str],
        attribute_name: str,
        raw_value: Any,
        source_fields: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        source_fields = source_fields or []
        if raw_value is None or pd.isna(raw_value):
            return self._make_result(raw_value, None, "unresolved", 0.0, "unresolved")

        raw_str = str(raw_value).strip()
        if not raw_str:
            return self._make_result(raw_value, None, "unresolved", 0.0, "unresolved")

        c_id = str(category_id).strip() if category_id and pd.notna(category_id) else ""
        norm_raw = self._normalize_text(raw_str)

        cache_key = f"{c_id}|{attribute_name}|{norm_raw}"
        if cache_key in self.resolution_cache:
            return self.resolution_cache[cache_key]

        # Category-Specific Attribute Restriction:
        # If category_id is specified and category_id or attribute_name is NOT in allowed attributes for that category -> REJECT!
        if c_id and (c_id not in self.category_allowed_attrs or attribute_name not in self.category_allowed_attrs[c_id]):
            res = self._make_result(raw_str, None, "unresolved", 0.0, "unresolved")
            self.resolution_cache[cache_key] = res
            return res

        # Filter LOV entries matching attribute_name
        candidate_entries = [e for e in self.lov_entries if e["attribute_name"] == attribute_name]
        allowed_canonical_vals = {e["canonical_value"] for e in candidate_entries}

        if not candidate_entries:
            res = self._make_result(raw_str, None, "unresolved", 0.0, "unresolved")
            self.resolution_cache[cache_key] = res
            return res

        # 1. Exact Match
        for e in candidate_entries:
            if raw_str == e["canonical_value"]:
                res = self._make_result(raw_str, e["canonical_value"], "exact", 1.0, "resolved")
                self.resolution_cache[cache_key] = res
                return res

        # 2. Normalized Match
        for e in candidate_entries:
            if norm_raw == e["normalized_value"]:
                res = self._make_result(raw_str, e["canonical_value"], "normalized", 0.95, "resolved")
                self.resolution_cache[cache_key] = res
                return res

        # 3. Unit Normalization (Separate UOM Master Engine)
        uom_res = self._try_unit_normalization(raw_str, attribute_name, candidate_entries)
        if uom_res:
            self.resolution_cache[cache_key] = uom_res
            return uom_res

        # 4. Numeric Normalization
        num_res = self._try_numeric_normalization(raw_str, candidate_entries)
        if num_res:
            self.resolution_cache[cache_key] = num_res
            return num_res

        # 5. Alias Match
        for e in candidate_entries:
            if norm_raw in e["aliases"]:
                res = self._make_result(raw_str, e["canonical_value"], "alias", 0.95, "resolved")
                self.resolution_cache[cache_key] = res
                return res

        # 6. Type-Aware Fuzzy Matching (DO NOT fuzzy match numeric/measurement specs!)
        attr_type = candidate_entries[0]["attribute_type"] if candidate_entries else "string"
        if attr_type not in ["integer", "float", "measurement"]:
            fuzzy_res = self._try_fuzzy_match(norm_raw, candidate_entries)
            if fuzzy_res:
                self.resolution_cache[cache_key] = fuzzy_res
                return fuzzy_res

        # 7. Gemini LLM Candidate Selection (Strictly Candidate-Constrained)
        if self.client is not None and not getattr(self, "llm_disabled", False):
            llm_res = self._call_llm_candidate_selector(c_id, attribute_name, raw_str, allowed_canonical_vals, source_fields)
            if llm_res and llm_res.get("canonical_value") in allowed_canonical_vals:
                self.resolution_cache[cache_key] = llm_res
                return llm_res

        # 8. Unresolved Fallback
        res = self._make_result(raw_str, None, "unresolved", 0.0, "unresolved")
        self.resolution_cache[cache_key] = res
        return res

    def _normalize_text(self, text: str) -> str:
        t = text.lower().strip()
        t = re.sub(r"\s+", " ", t)
        t = t.strip('"\'')
        return t

    def _try_unit_normalization(self, raw_str: str, attr_name: str, candidate_entries: List[dict]) -> Optional[dict]:
        norm_lower = raw_str.lower().strip()
        if norm_lower in self.uom_map:
            canon_uom = self.uom_map[norm_lower]
            for e in candidate_entries:
                if e["canonical_value"].lower() == canon_uom.lower() or e["normalized_value"] == canon_uom.lower():
                    return self._make_result(raw_str, e["canonical_value"], "unit_normalization", 0.98, "resolved")

        m = re.match(r"^(\d+(?:\.\d+)?|\d+/\d+)\s*([a-zA-Z\"']+)?$", raw_str)
        if m:
            val_part = m.group(1)
            unit_part = m.group(2)
            if unit_part and unit_part.lower() in self.uom_map:
                norm_uom = self.uom_map[unit_part.lower()]
                combo_val = f"{val_part} {norm_uom}".lower()
                combo_val_alt = f"{val_part}{norm_uom}".lower()
                for e in candidate_entries:
                    e_norm = e["normalized_value"]
                    if e_norm in [combo_val, combo_val_alt, norm_lower]:
                        return self._make_result(raw_str, e["canonical_value"], "unit_normalization", 0.98, "resolved")
        return None

    def _try_numeric_normalization(self, raw_str: str, candidate_entries: List[dict]) -> Optional[dict]:
        try:
            val_num = float(re.sub(r"[^\d.]", "", raw_str))
            int_val = int(val_num) if val_num.is_integer() else val_num
            int_str = str(int_val)

            for e in candidate_entries:
                if e["canonical_value"] == int_str or e["normalized_value"] == int_str:
                    return self._make_result(raw_str, e["canonical_value"], "numeric_normalization", 0.98, "resolved")
        except Exception:
            pass
        return None

    def _try_fuzzy_match(self, norm_raw: str, candidate_entries: List[dict]) -> Optional[dict]:
        cand_map = {e["normalized_value"]: e["canonical_value"] for e in candidate_entries}
        cand_keys = list(cand_map.keys())

        if not cand_keys:
            return None

        match = process.extractOne(norm_raw, cand_keys, scorer=fuzz.WRatio)
        if match:
            best_key, score, _ = match
            if score >= 95:
                return self._make_result(norm_raw, cand_map[best_key], "fuzzy", round(score / 100.0, 4), "resolved")
            elif 90 <= score < 95:
                matches = process.extract(norm_raw, cand_keys, scorer=fuzz.WRatio, limit=2)
                if len(matches) > 1 and abs(matches[0][1] - matches[1][1]) < 3:
                    return self._make_result(norm_raw, None, "fuzzy", round(score / 100.0, 4), "ambiguous")
                return self._make_result(norm_raw, cand_map[best_key], "fuzzy", round(score / 100.0, 4), "resolved")
        return None

    def _call_llm_candidate_selector(
        self,
        c_id: str,
        attr_name: str,
        raw_str: str,
        allowed_canonical_vals: Set[str],
        source_fields: List[Any]
    ) -> Optional[dict]:
        if not self.client or getattr(self, "llm_disabled", False):
            return None

        self.llm_stats["calls"] += 1
        cand_list = sorted(list(allowed_canonical_vals))

        prompt = f"""You are a controlled LOV candidate selector.
Category: '{c_id}'
Attribute: '{attr_name}'
Raw Input Value: "{raw_str}"
Source Context: "{' '.join([str(f) for f in source_fields if f])}"

Allowed Candidate LOV Values (DO NOT select any value outside this list):
{json.dumps(cand_list)}

Instructions:
Select the exact candidate from the allowed list that matches the raw input value.
If no candidate matches, return null.

Return ONLY valid JSON:
{{
  "selected_value": "<ONE_EXACT_CANDIDATE_OR_NULL>",
  "confidence": 0.90
}}
"""
        try:
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
                sel_val = parsed.get("selected_value")
                conf = float(parsed.get("confidence", 0.90))

                if sel_val and sel_val in allowed_canonical_vals:
                    self.llm_stats["accepted"] += 1
                    return self._make_result(raw_str, sel_val, "llm", round(conf, 4), "resolved")
                else:
                    self.llm_stats["rejected"] += 1
        except Exception as e:
            err_msg = str(e)
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                logger.warning("LLM API daily quota exhausted. Disabling further LLM calls for this session.")
                self.llm_disabled = True
            else:
                logger.warning(f"LLM candidate selection failed: {e}")
            self.llm_stats["rejected"] += 1

        return None

    def _make_result(self, raw_val: Any, canon_val: Optional[str], method: str, conf: float, status: str) -> dict:
        return {
            "raw_value": str(raw_val) if raw_val is not None else None,
            "canonical_value": canon_val,
            "method": method,
            "confidence": conf,
            "status": status
        }
