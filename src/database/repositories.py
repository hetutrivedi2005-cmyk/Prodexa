import os
import json
import glob
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.database.connection import db_manager, BASE_DIR
from src.database.models import ProductModel, ReviewQueueModel, ReviewActionModel

class DatabaseRepository:
    """
    Production Repository abstraction for PRODEXA PostgreSQL database & fallback layer.
    """
    def __init__(self):
        self.conn = db_manager

    # ---------------------------------------------------------
    # PRODUCTS & ATTRIBUTES
    # ---------------------------------------------------------
    def get_products(self, search: Optional[str] = None, brand: Optional[str] = None,
                     manufacturer: Optional[str] = None, product_type: Optional[str] = None,
                     validation_status: Optional[str] = None, min_confidence: Optional[float] = None,
                     max_confidence: Optional[float] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        
        # 1. Supabase Client Query
        if self.conn.is_connected() and self.conn.client:
            try:
                query = self.conn.client.from_("products").select("*, product_attributes(*), validations(*), confidence_scores(*)", count="exact")
                if search:
                    query = query.or_(f"mpn.ilike.%{search}%,brand.ilike.%{search}%,manufacturer.ilike.%{search}%,product_type.ilike.%{search}%")
                if brand:
                    query = query.eq("brand", brand)
                if manufacturer:
                    query = query.eq("manufacturer", manufacturer)
                if product_type:
                    query = query.eq("product_type", product_type)
                if validation_status:
                    query = query.eq("validation_status", validation_status)
                if min_confidence is not None:
                    query = query.gte("confidence_score", min_confidence)
                if max_confidence is not None:
                    query = query.lte("confidence_score", max_confidence)
                    
                start = (page - 1) * limit
                end = start + limit - 1
                res = query.range(start, end).execute()
                
                # Fetch available filter options
                brands_res = self.conn.client.from_("products").select("brand").not_.is_("brand", "null").execute()
                types_res = self.conn.client.from_("products").select("product_type").not_.is_("product_type", "null").execute()
                
                brands = sorted(list(set(b["brand"] for b in (brands_res.data or []) if b.get("brand"))))
                types = sorted(list(set(t["product_type"] for t in (types_res.data or []) if t.get("product_type"))))
                
                return {
                    "total": res.count or len(res.data or []),
                    "page": page,
                    "limit": limit,
                    "pages": ((res.count or len(res.data or [])) + limit - 1) // limit if limit else 1,
                    "items": res.data or [],
                    "available_filters": {"brands": brands, "product_types": types}
                }
            except Exception as e:
                print(f"[SupabaseRepository] Supabase query fallback ({e})")

        # 2. Local Dataset Query Fallback
        p_file = BASE_DIR / "data" / "final" / "product.json"
        products = []
        if p_file.exists():
            try:
                with open(p_file, "r", encoding="utf-8") as f:
                    products = json.load(f)
            except Exception:
                pass

        filtered = []
        for item in products:
            p_info = item.get("product", {})
            val_info = item.get("validation", {})
            
            if search:
                q = search.lower()
                text_space = f"{p_info.get('product_id','')} {p_info.get('mpn','')} {p_info.get('brand','')} {p_info.get('manufacturer','')} {p_info.get('product_type','')}".lower()
                if q not in text_space:
                    continue
            if brand and p_info.get("brand", "").lower() != brand.lower():
                continue
            if manufacturer and p_info.get("manufacturer", "").lower() != manufacturer.lower():
                continue
            if product_type and p_info.get("product_type", "").lower() != product_type.lower():
                continue
            if validation_status and val_info.get("status", "").lower() != validation_status.lower():
                continue
                
            conf = float(val_info.get("confidence", 0.0))
            if min_confidence is not None and conf < min_confidence:
                continue
            if max_confidence is not None and conf > max_confidence:
                continue
                
            filtered.append(item)

        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        
        all_brands = sorted(list(set(p.get("product", {}).get("brand") for p in products if p.get("product", {}).get("brand"))))
        all_types = sorted(list(set(p.get("product", {}).get("product_type") for p in products if p.get("product", {}).get("product_type"))))

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if limit else 1,
            "items": filtered[start:end],
            "available_filters": {"brands": all_brands, "product_types": all_types}
        }

    def get_product_detail(self, product_id: str) -> Optional[Dict[str, Any]]:
        if self.conn.is_connected() and self.conn.client:
            try:
                res = self.conn.client.from_("products").select("*, product_attributes(*), evidence(*), validations(*), confidence_scores(*), product_descriptions(*), review_queue(*)").or_(f"source_product_id.eq.{product_id},mpn.eq.{product_id}").execute()
                if res.data:
                    return res.data[0]
            except Exception:
                pass

        p_file = BASE_DIR / "data" / "final" / "product.json"
        if not p_file.exists():
            return None
            
        with open(p_file, "r", encoding="utf-8") as f:
            products = json.load(f)

        for p in products:
            if p.get("product", {}).get("product_id") == product_id or p.get("product", {}).get("mpn") == product_id:
                return p
        return None

    # ---------------------------------------------------------
    # EVIDENCE
    # ---------------------------------------------------------
    def get_evidence(self, product_id: Optional[str] = None, verification_status: Optional[str] = None,
                     page: int = 1, limit: int = 30) -> Dict[str, Any]:
        ev_file = BASE_DIR / "data" / "final" / "evidence.json"
        evidence_list = []
        if ev_file.exists():
            try:
                with open(ev_file, "r", encoding="utf-8") as f:
                    evidence_list = json.load(f)
            except Exception:
                pass

        filtered = []
        for item in evidence_list:
            if product_id and item.get("product_id") != product_id:
                continue
            if verification_status and item.get("verification_status") != verification_status:
                continue
            filtered.append(item)

        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": filtered[start:end]
        }

    # ---------------------------------------------------------
    # REVIEW QUEUE & AUDIT TRAIL
    # ---------------------------------------------------------
    def get_review_queue(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        q_file = BASE_DIR / "data" / "review" / "review_queue.jsonl"
        items = []
        if q_file.exists():
            try:
                with open(q_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            d = json.loads(line)
                            if status_filter:
                                if d.get("review_status") == status_filter:
                                    items.append(d)
                            else:
                                items.append(d)
            except Exception:
                pass
        return items

    def record_review_action(self, review_id: str, action: str, actor_id: str,
                              old_val: Optional[str], new_val: Optional[str], comment: Optional[str]) -> Dict[str, Any]:
        # Log to audit stream file
        audit_file = BASE_DIR / "data" / "review" / "review_audit.jsonl"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        audit_entry = {
            "audit_id": f"AUD-{int(time.time()*1000)}",
            "review_id": review_id,
            "action": action,
            "actor_id": actor_id,
            "previous_val": old_val,
            "new_val": new_val,
            "reason": comment,
            "created_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
        
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_entry) + "\n")
            
        return audit_entry

# Global repository instance
repo = DatabaseRepository()
