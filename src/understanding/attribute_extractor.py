import os
import re
import json
import logging
import pandas as pd
from typing import Optional, Dict, Tuple, List, Set, Any
import dotenv
from google import genai
from google.genai import types

from src.understanding.attribute_schema import AttributeItem, ExtractedAttributesPayload

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


def ground_text_in_fields(value: str, evidence_token: str, source_fields: List[Any]) -> bool:
    """
    Evidence Grounding Check:
    Verifies if the extracted value or raw evidence token appears physically in at least one source field text.
    Inspects part_desc, size, quantity, product_type, brand, manufacturer, mfg_part_num, manufacturer_part_number.
    """
    if not evidence_token and not value:
        return False

    ev_str = str(evidence_token).strip().lower()
    val_str = str(value).strip().lower()

    for field in source_fields:
        if field is None or pd.isna(field):
            continue
        f_str = str(field).strip().lower()
        if not f_str:
            continue
        if ev_str in f_str or val_str in f_str:
            return True

    return False


class CategoryAttributeExtractor:
    """
    Part 3 — Category Attribute Extractor (Semantically Precise & Quality-Improved)
    Rule-first deterministic extraction + LLM candidate fallback + Pydantic validation + Evidence Grounding across ALL source fields.
    """

    def __init__(self, schema_csv_path: str = "data/master/category_attributes.csv", client: Optional[genai.Client] = None):
        self.schema_csv_path = schema_csv_path

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

        self.llm_stats = {
            "calls": 0,
            "accepted": 0,
            "rejected": 0,
            "null": 0
        }

        self.category_schemas: Dict[str, Dict[str, dict]] = {}
        self.extraction_cache: Dict[str, dict] = {}
        self._load_schema()

    def _load_schema(self):
        if not os.path.exists(self.schema_csv_path):
            raise FileNotFoundError(f"Attribute master '{self.schema_csv_path}' not found! Run schema builder first.")

        df = pd.read_csv(self.schema_csv_path)
        for _, r in df.iterrows():
            c_id = str(r['category_id']).strip()
            a_id = str(r['attribute_id']).strip()

            if c_id not in self.category_schemas:
                self.category_schemas[c_id] = {}

            self.category_schemas[c_id][a_id] = {
                "attribute_id": a_id,
                "attribute_name": str(r['attribute_name']).strip(),
                "attribute_type": str(r['attribute_type']).strip(),
                "is_required": bool(r['is_required']),
                "unit_of_measure": str(r['unit_of_measure']).strip() if pd.notna(r['unit_of_measure']) else "",
                "allowed_values": [v.strip() for v in str(r['allowed_values']).split(';') if v.strip()] if pd.notna(r['allowed_values']) else [],
                "extraction_keywords": [k.strip() for k in str(r['extraction_keywords']).split(';') if k.strip()] if pd.notna(r['extraction_keywords']) else [],
                "aliases": [a.strip() for a in str(r['aliases']).split(';') if a.strip()] if pd.notna(r['aliases']) else []
            }

    def extract_product_attributes(
        self,
        category_id: Optional[str],
        part_desc: Optional[str],
        size: Optional[str] = None,
        quantity: Optional[str] = None,
        product_type: Optional[str] = None,
        brand: Optional[str] = None,
        manufacturer: Optional[str] = None,
        mfg_part_num: Optional[str] = None
    ) -> Dict[str, Any]:
        source_fields = [part_desc, size, quantity, product_type, brand, manufacturer, mfg_part_num]
        desc_text = f"{str(part_desc or '')} {str(size or '')} {str(quantity or '')} {str(product_type or '')}".strip()

        cache_key = f"{category_id}|{desc_text}|{brand}"
        if cache_key in self.extraction_cache:
            return self.extraction_cache[cache_key]

        c_id = str(category_id).strip() if category_id and pd.notna(category_id) else ""
        allowed_schema = self.category_schemas.get(c_id, {})

        empty_res = {
            "extracted_attributes_json": json.dumps({}),
            "attribute_extraction_status": "none",
            "attribute_extraction_method": "none",
            "attribute_confidence": 0.0,
            "attribute_validation_status": "invalid"
        }

        if not allowed_schema or not desc_text:
            return empty_res

        extracted_attrs: Dict[str, dict] = {}
        used_methods = set()

        # =========================================================================
        # Stage 1: Deterministic Extraction Rules (Semantically Precise)
        # =========================================================================
        # 1. Grit Extraction (Abrasives)
        if "grit" in allowed_schema:
            grit_m = re.search(r"\b(P\d{2,3})\b", desc_text, re.IGNORECASE)
            if grit_m:
                g_val = grit_m.group(1).upper()
                if ground_text_in_fields(g_val, grit_m.group(0), source_fields):
                    extracted_attrs["grit"] = {
                        "value": g_val,
                        "confidence": 1.00,
                        "evidence": grit_m.group(0),
                        "method": "rule"
                    }
                    used_methods.add("rule")

        # 2. Dimensions (Width x Length multi-dimensional specs, e.g. 1/2 in x 18 in, 2.75 in x 30 in)
        if "dimensions" in allowed_schema:
            if size and pd.notna(size) and ("x" in str(size).lower() or "in" in str(size).lower()):
                sz_str = str(size).strip()
                extracted_attrs["dimensions"] = {
                    "value": sz_str,
                    "confidence": 1.00,
                    "evidence": sz_str,
                    "method": "rule"
                }
                used_methods.add("rule")
            else:
                dim_m = re.search(r"\b(\d+/\d+(?:\s*in)?\s*x\s*\d+(?:\s*in)?|\d+(?:\.\d+)?\s*x\s*\d+(?:\.\d+)?)\b", desc_text, re.IGNORECASE)
                if dim_m:
                    d_val = dim_m.group(1).strip()
                    if not d_val.endswith("in") and not d_val.endswith('"'):
                        d_val = f"{d_val} in"
                    if ground_text_in_fields(d_val, dim_m.group(0), source_fields):
                        extracted_attrs["dimensions"] = {
                            "value": d_val,
                            "confidence": 0.98,
                            "evidence": dim_m.group(0),
                            "method": "rule"
                        }
                        used_methods.add("rule")

        # 3. Disc Diameter (Circular Discs ONLY, e.g. 5 in, 9 in, 12 in, 14 in, 4 in, 7 in)
        if "diameter" in allowed_schema and "diameter" not in extracted_attrs:
            if size and pd.notna(size) and "x" not in str(size).lower() and str(size).strip():
                sz_str = str(size).strip()
                extracted_attrs["diameter"] = {
                    "value": sz_str,
                    "confidence": 1.00,
                    "evidence": sz_str,
                    "method": "rule"
                }
                used_methods.add("rule")

            if "diameter" not in extracted_attrs:
                dia_m = re.search(r"\b(\d+(?:\.\d+)?|\d+-\d+/\d+)\s*(?:in|\"|inch)\b", desc_text, re.IGNORECASE)
                if dia_m and "x" not in dia_m.group(0).lower():
                    d_val = f"{dia_m.group(1).strip()} in"
                    if ground_text_in_fields(d_val, dia_m.group(0), source_fields):
                        extracted_attrs["diameter"] = {
                            "value": d_val,
                            "confidence": 0.98,
                            "evidence": dia_m.group(0),
                            "method": "rule"
                        }
                        used_methods.add("rule")

        # 4. Voltage Extraction (Tools & Electrical)
        if "voltage" in allowed_schema:
            volt_m = re.search(r"\b(\d{1,3}\s*V)\b", desc_text, re.IGNORECASE)
            if volt_m:
                v_val = volt_m.group(1).upper().replace(" ", "")
                if ground_text_in_fields(v_val, volt_m.group(0), source_fields):
                    extracted_attrs["voltage"] = {
                        "value": v_val,
                        "confidence": 0.99,
                        "evidence": volt_m.group(0),
                        "method": "rule"
                    }
                    used_methods.add("rule")

        # 5. Wattage Extraction (Lighting ONLY)
        if "wattage" in allowed_schema:
            watt_m = re.search(r"\b(\d{1,3}\s*W)\b", desc_text, re.IGNORECASE)
            if watt_m:
                w_val = watt_m.group(1).upper().replace(" ", "")
                if ground_text_in_fields(w_val, watt_m.group(0), source_fields):
                    extracted_attrs["wattage"] = {
                        "value": w_val,
                        "confidence": 0.99,
                        "evidence": watt_m.group(0),
                        "method": "rule"
                    }
                    used_methods.add("rule")

        # 6. Color Temperature (27K Rule for Lighting ONLY)
        if "color_temperature" in allowed_schema:
            cct_m = re.search(r"\b(27K|30K|40K|50K|2700K|3000K|5000K)\b", desc_text, re.IGNORECASE)
            if cct_m:
                raw_cct = cct_m.group(1).upper()
                cct_val = "2700K" if raw_cct == "27K" else ("3000K" if raw_cct == "30K" else ("5000K" if raw_cct == "50K" else raw_cct))
                if ground_text_in_fields(raw_cct, cct_m.group(0), source_fields):
                    extracted_attrs["color_temperature"] = {
                        "value": cct_val,
                        "confidence": 0.98,
                        "evidence": cct_m.group(0),
                        "method": "rule"
                    }
                    used_methods.add("rule")

        # 7. Drive Size (Tool Accessories)
        if "drive_size" in allowed_schema:
            drv_m = re.search(r"\b(1/4|3/8|1/2)\s*(?:in|\")?\s*Drive\b", desc_text, re.IGNORECASE)
            if drv_m:
                drv_val = f"{drv_m.group(1)} in"
                if ground_text_in_fields(drv_m.group(1), drv_m.group(0), source_fields):
                    extracted_attrs["drive_size"] = {
                        "value": drv_val,
                        "confidence": 0.99,
                        "evidence": drv_m.group(0),
                        "method": "rule"
                    }
                    used_methods.add("rule")

        # 8. Pack Quantity / Piece Count
        if "pack_quantity" in allowed_schema or "piece_count" in allowed_schema:
            q_attr = "pack_quantity" if "pack_quantity" in allowed_schema else "piece_count"

            if quantity and pd.notna(quantity) and str(quantity).strip():
                try:
                    q_num = int(float(quantity))
                    if q_num > 0:
                        extracted_attrs[q_attr] = {
                            "value": q_num,
                            "confidence": 1.00,
                            "evidence": str(quantity),
                            "method": "rule"
                        }
                        used_methods.add("rule")
                except Exception:
                    pass

            if q_attr not in extracted_attrs:
                pq_m = re.search(r"\b(\d+)\s*(?:pc|pcs|pk|pack|Disc/Box)\b", desc_text, re.IGNORECASE)
                if pq_m:
                    pq_val = int(pq_m.group(1))
                    if ground_text_in_fields(pq_m.group(1), pq_m.group(0), source_fields):
                        extracted_attrs[q_attr] = {
                            "value": pq_val,
                            "confidence": 0.98,
                            "evidence": pq_m.group(0),
                            "method": "rule"
                        }
                        used_methods.add("rule")

        # 9. Material Abbreviation Normalization (SS -> Stainless Steel, BRS -> Brass, AL -> Aluminum, PVC -> PVC)
        if "color_finish" in allowed_schema or "material" in allowed_schema:
            target_attr = "color_finish" if "color_finish" in allowed_schema else "material"
            if target_attr not in extracted_attrs:
                mat_m = re.search(r"\b(SS|BRS|AL|PVC|Stainless Steel)\b", desc_text, re.IGNORECASE)
                if mat_m:
                    raw_mat = mat_m.group(1).upper()
                    norm_mat = "Stainless Steel" if raw_mat == "SS" else ("Brass" if raw_mat == "BRS" else ("Aluminum" if raw_mat == "AL" else "PVC"))
                    if ground_text_in_fields(raw_mat, mat_m.group(0), source_fields):
                        extracted_attrs[target_attr] = {
                            "value": norm_mat,
                            "confidence": 0.98,
                            "evidence": mat_m.group(0),
                            "method": "rule"
                        }
                        used_methods.add("rule")

        # =========================================================================
        # Stage 2: Gemini LLM Extraction Fallback
        # =========================================================================
        missing_allowed_keys = [k for k in allowed_schema.keys() if k not in extracted_attrs]
        if missing_allowed_keys and self.client is not None and not getattr(self, "llm_disabled", False):
            llm_attrs = self._call_llm_attribute_extractor(desc_text, allowed_schema, source_fields)
            if llm_attrs:
                for a_key, a_item in llm_attrs.items():
                    if a_key in allowed_schema and a_key not in extracted_attrs:
                        extracted_attrs[a_key] = a_item
                        used_methods.add("llm")

        # =========================================================================
        # Stage 3: Pydantic Validation & Evidence Grounding Check
        # =========================================================================
        validated_attrs: Dict[str, dict] = {}
        for a_key, a_data in extracted_attrs.items():
            if a_key not in allowed_schema:
                continue

            is_grounded = ground_text_in_fields(str(a_data["value"]), str(a_data["evidence"]), source_fields)
            if not is_grounded:
                continue

            try:
                item_obj = AttributeItem(
                    value=a_data["value"],
                    confidence=float(a_data["confidence"]),
                    evidence=str(a_data["evidence"]),
                    method=a_data["method"]
                )
                validated_attrs[a_key] = item_obj.model_dump()
            except Exception as val_e:
                logger.debug(f"Pydantic validation failed for attribute '{a_key}': {val_e}")

        num_allowed = len(allowed_schema)
        num_extracted = len(validated_attrs)

        if num_extracted == 0:
            status_val = "none"
            method_val = "none"
            validation_val = "invalid"
            avg_conf = 0.0
        elif num_extracted >= min(2, num_allowed):
            status_val = "complete"
            method_val = "hybrid" if len(used_methods) > 1 else ("rule" if "rule" in used_methods else "llm")
            validation_val = "valid"
            avg_conf = float(pd.Series([v["confidence"] for v in validated_attrs.values()]).mean())
        else:
            status_val = "partial"
            method_val = "rule" if "rule" in used_methods else "llm"
            validation_val = "partial"
            avg_conf = float(pd.Series([v["confidence"] for v in validated_attrs.values()]).mean())

        res = {
            "extracted_attributes_json": json.dumps(validated_attrs),
            "attribute_extraction_status": status_val,
            "attribute_extraction_method": method_val,
            "attribute_confidence": round(avg_conf, 4),
            "attribute_validation_status": validation_val
        }

        self.extraction_cache[cache_key] = res
        return res

    def _call_llm_attribute_extractor(self, desc_text: str, allowed_schema: Dict[str, dict], source_fields: List[Any]) -> Dict[str, dict]:
        """
        Gemini LLM Extraction Fallback.
        STRICT REQUIREMENT: Returns ONLY JSON matching allowed attributes defined in category_attributes.csv.
        """
        if not self.client or getattr(self, "llm_disabled", False):
            return {}

        self.llm_stats["calls"] += 1

        schema_info = []
        for a_id, a_meta in allowed_schema.items():
            schema_info.append(f"- Attribute: '{a_id}' | Type: {a_meta['attribute_type']} | Unit: '{a_meta['unit_of_measure']}' | Allowed: {a_meta['allowed_values']}")

        prompt = f"""You are a catalog attribute extraction engine.
Product Source Text: "{desc_text}"

Allowed Category Attribute List (DO NOT extract any attribute outside this list):
{chr(10).join(schema_info)}

Instructions:
Extract key-value product attributes strictly supported by evidence in the source text.
Return ONLY valid JSON matching this structure:
{{
  "attributes": {{
    "<ALLOWED_ATTRIBUTE_ID>": {{
      "value": "<EXTRACTED_VALUE>",
      "confidence": 0.90,
      "evidence": "<EXACT_SOURCE_TEXT_SUBSTRING>",
      "method": "llm"
    }}
  }}
}}

If no allowed attributes can be extracted, return {{"attributes": {{}}}}.
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
                attrs_dict = parsed.get("attributes", {})
                valid_llm_attrs = {}

                for a_key, a_val in attrs_dict.items():
                    if a_key in allowed_schema and isinstance(a_val, dict):
                        e_text = str(a_val.get("evidence", "")).strip()
                        v_text = str(a_val.get("value", "")).strip()
                        if ground_text_in_fields(v_text, e_text, source_fields):
                            valid_llm_attrs[a_key] = {
                                "value": a_val.get("value"),
                                "confidence": float(a_val.get("confidence", 0.85)),
                                "evidence": e_text,
                                "method": "llm"
                            }
                if valid_llm_attrs:
                    self.llm_stats["accepted"] += 1
                else:
                    self.llm_stats["null"] += 1
                return valid_llm_attrs
        except Exception as e:
            err_msg = str(e)
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                logger.warning("LLM API daily quota exhausted. Disabling further LLM calls for this session.")
                self.llm_disabled = True
            else:
                logger.warning(f"LLM attribute extraction failed: {e}")
            self.llm_stats["rejected"] += 1

        return {}
