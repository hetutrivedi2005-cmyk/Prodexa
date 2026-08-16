import re
from typing import Optional, List, Tuple, Dict
from src.understanding.schema import ProductInfo, clean_value, clean_string_value


class ProductNormalizer:
    """
    Modular Normalization, Consistency, and Status Layer for Product Info.
    """

    GRIT_PATTERNS = re.compile(r"\bP\d{2,4}\b", re.IGNORECASE)
    KNOWN_GRIT_NUMBERS = {40, 60, 80, 100, 120, 150, 180, 220, 240, 320, 400, 600, 800, 1000, 1200}

    @staticmethod
    def normalize_dimensions(size_str: Optional[str], raw_desc: str = "") -> Optional[str]:
        """
        Normalizes dimension formatting conservatively.
        Examples:
            1/2"x18" -> 1/2 in x 18 in
            5" -> 5 in
            7-1/4" -> 7-1/4 in
            2.75x30 -> 2.75 in x 30 in
            1x6-16' -> 1 in x 6 in x 16 ft
            6'x36" -> 6 ft x 36 in
            6' -> 6 ft
        """
        size_str = clean_value(size_str)
        target = size_str or raw_desc
        if not target:
            return None

        # 1. Match lumber board dimensions: 1x6-16' -> 1 in x 6 in x 16 ft
        lumber_match = re.search(r"(\d+)\s*x\s*(\d+)\s*-\s*(\d+)\s*(?:'|ft)", target, re.IGNORECASE)
        if lumber_match:
            return f"{lumber_match.group(1)} in x {lumber_match.group(2)} in x {lumber_match.group(3)} ft"

        # 2. Match feet x inches range: 6'x36" -> 6 ft x 36 in
        feet_in_match = re.search(r"(\d+)\s*'\s*x\s*(\d+)\s*(?:\"|in)", target, re.IGNORECASE)
        if feet_in_match:
            return f"{feet_in_match.group(1)} ft x {feet_in_match.group(2)} in"

        # 3. Match decimal range dimensions: 2.75x30 or 2.75 in x 30 in
        dec_match = re.search(r"(\d+\.\d+)\s*(?:\"|in|inch|inches)?\s*x\s*(\d+(?:\.\d+)?)\s*(?:\"|in|inch|inches)?", target, re.IGNORECASE)
        if dec_match and "x" in target.lower():
            return f"{dec_match.group(1)} in x {dec_match.group(2)} in"

        # 4. Match fractional dimensions: 1/2"x18" or 7-1/4" x 18"
        frac_range_match = re.search(r"(\d+(?:-\d+/\d+|\s+\d+/\d+|/\d+))\s*(?:\"|in|inch|inches)?\s*x\s*(\d+(?:-\d+/\d+|\s+\d+/\d+|/\d+|\.\d+)?)\s*(?:\"|in|inch|inches)?", target, re.IGNORECASE)
        if frac_range_match and "x" in target.lower():
            return f"{frac_range_match.group(1).strip()} in x {frac_range_match.group(2).strip()} in"

        # 5. Match single dimension with inches: 7-1/4" or 5" or 5 inch or 5 in
        single_match = re.search(r"(\d+(?:-\d+/\d+|\s+\d+/\d+|/\d+|\.\d+)?)\s*(?:\"|in\b|inch\b|inches\b)", target, re.IGNORECASE)
        if single_match:
            d_val = single_match.group(1).strip()
            if not re.search(rf"\b{re.escape(d_val)}\s*(?:V|Ah|P)\b", target, re.IGNORECASE):
                return f"{d_val} in"

        # 6. Match single feet dimension: 6' or 8' or 16'
        single_feet = re.search(r"\b(\d+)\s*'\b", target)
        if single_feet:
            return f"{single_feet.group(1)} ft"

        if size_str:
            clean_s = re.sub(r"\b(inches|inch)\b", "in", size_str, flags=re.IGNORECASE)
            return clean_value(clean_s)

        return None

    @classmethod
    def extract_quantity(cls, raw_desc: str, candidate_qty: Optional[int] = None) -> Optional[int]:
        """
        Strictly validates or extracts package quantity:
        - 20V -> Voltage (NOT quantity 20)
        - 8Ah -> Battery capacity (NOT quantity 8)
        - P80 / P120 -> Grit (NOT quantity 80 / 120)
        - 2pk / 2 pack / 6pc / 50 Disc/Box -> Package Count (Quantity 2 / 6 / 50)
        """
        if not raw_desc:
            return None

        desc_clean = raw_desc.strip()

        # 1. Match explicit package count patterns in raw_desc
        pkg_match = re.search(r"\b(\d+)\s*(?:pk|pack|-pack|pc|pcs|piece|pieces|disc/box|discs/box|per box|box)\b", desc_clean, re.IGNORECASE)
        if pkg_match:
            val = int(pkg_match.group(1))
            if 1 <= val <= 1000:
                return val

        pk_prefix = re.search(r"\bPK(\d+)\b", desc_clean, re.IGNORECASE)
        if pk_prefix:
            val = int(pk_prefix.group(1))
            if 1 <= val <= 1000:
                return val

        # 2. If candidate_qty was provided by Gemini/schema validation:
        if candidate_qty is not None and isinstance(candidate_qty, int) and candidate_qty >= 1:
            if re.search(rf"\b{candidate_qty}\s*V\b", desc_clean, re.IGNORECASE):
                return None
            if re.search(rf"\b{candidate_qty}\s*Ah\b", desc_clean, re.IGNORECASE):
                return None
            if re.search(rf"\bP{candidate_qty}\b", desc_clean, re.IGNORECASE):
                return None
            if re.search(rf"\b{candidate_qty}\s*(?:\"|in|inch|inches|mm|cm)\b", desc_clean, re.IGNORECASE):
                return None

            if re.search(rf"\b{candidate_qty}\s*(?:pk|pack|-pack|pc|pcs|piece|pieces|disc/box|discs/box|per box|box)\b", desc_clean, re.IGNORECASE):
                return candidate_qty

        return None

    @classmethod
    def sanitize_attributes(cls, info: ProductInfo, raw_desc: str) -> ProductInfo:
        """
        Sanitizes individual product fields using clean_value, ensuring grit ratings
        and voltages are not quantity and dimensions are normalized cleanly.
        """
        mpn = clean_value(info.manufacturer_part_number)
        brand = clean_value(info.brand)
        product_type = clean_value(info.product_type)
        size = cls.normalize_dimensions(info.size, raw_desc)
        quantity = cls.extract_quantity(raw_desc, info.quantity)

        return ProductInfo(
            manufacturer_part_number=mpn,
            brand=brand,
            product_type=product_type,
            size=size,
            quantity=quantity,
            understanding_status=info.understanding_status,
            confidence=info.confidence
        )

    @classmethod
    def deterministic_fallback_extract(cls, raw_desc: str) -> Optional[ProductInfo]:
        """
        Comprehensive deterministic fallback extractor for tool, hardware, and industrial product descriptions.
        """
        if not raw_desc or not raw_desc.strip():
            return None
        desc = raw_desc.strip()

        # 1. MPN extraction
        mpn = None
        tokens = desc.split()
        if tokens:
            first_tok = tokens[0]
            if first_tok.upper() == "3M" and len(tokens) > 1 and re.match(r"^[A-Z0-9]+$", tokens[1], re.IGNORECASE):
                mpn = clean_value(tokens[1])
            elif re.match(r"^[A-Z0-9]+(?:[.\-][A-Z0-9]+)*$", first_tok, re.IGNORECASE) and len(first_tok) >= 3:
                # Exclude plain dimension numbers like 3/4x60 or 1x6-16'
                if not re.match(r"^\d+(?:/\d+)?x\d+", first_tok, re.IGNORECASE) and not re.match(r"^\d+x\d+-\d+", first_tok, re.IGNORECASE) and not re.match(r"^\d+'", first_tok):
                    mpn = clean_value(first_tok)

        # 2. Brand extraction
        brand = None
        brand_map = [
            (r"\bmilw(?:aukee)?\b", "Milwaukee"),
            (r"\bdewalt\b", "Dewalt"),
            (r"\bfestool\b", "Festool"),
            (r"\bdremel\b", "Dremel"),
            (r"\bgrizzly\b", "Grizzly"),
            (r"\boliver\b", "Oliver"),
            (r"\bazek\b", "Azek"),
            (r"\btimbertech\b", "TimberTech"),
            (r"\btrex\b", "Trex"),
            (r"\bspeed\s*queen\b|\bsq\s+(?:elect|gas|washer|dryer)\b", "Speed Queen"),
            (r"\bkitchen\s*aid\b", "KitchenAid"),
            (r"\blg\b", "LG"),
            (r"\bge\b", "GE"),
            (r"\bkreg\b", "Kreg"),
            (r"\bdiablo\b", "Diablo"),
            (r"\b3m\b", "3M"),
            (r"\bmirka\b", "Mirka"),
            (r"\bhiolit\b", "HIOLIT"),
            (r"\babranet\b", "Abranet"),
            (r"\bbosch\b", "Bosch"),
            (r"\bmakita\b", "Makita"),
            (r"\bryobi\b", "Ryobi"),
            (r"\bcraftsman\b", "Craftsman"),
            (r"\bking\b", "King Industrial"),
            (r"\bsteff\b", "Steff")
        ]
        desc_lower = desc.lower()
        for b_regex, b_name in brand_map:
            if re.search(b_regex, desc_lower):
                brand = b_name
                break

        # 3. Product Type extraction
        product_type = None
        type_patterns = [
            (r"\bcirc(?:ular)?\s*-\s*saw\s*kit\b|\bcirc\s*saw\s*kit\b", "Circular Saw Kit"),
            (r"\bcirc(?:ular)?\s*saw\b|\bmetal\s*cutting\s*circ\s*saw\b", "Circular Saw"),
            (r"\bjig\s*saw\b|\bjigsaw\b", "Jig Saw"),
            (r"\brotary\s*tool\b", "Rotary Tool"),
            (r"\b(?:elect(?:ric)?\s*)?dryer\b", "Electric Dryer"),
            (r"\bwasher\b", "Washer"),
            (r"\blaundry\s*center\b", "Laundry Center"),
            (r"\bheater\s*kit\b|\bheater\b", "Heater Kit"),
            (r"\brail(?:ing)?\s*kit\b|\brail\b", "Railing Kit"),
            (r"\bdecking\b", "Decking"),
            (r"\bbattery\b", "Battery Pack" if "2pk" in desc_lower or "pk" in desc_lower else "Battery"),
            (r"\bcharger\b", "Battery Charger"),
            (r"\borganizer\b", "Organizer"),
            (r"\bplaner\b", "Planer"),
            (r"\bjointer\b", "Jointer"),
            (r"\bshaper\b", "Shaper"),
            (r"\bfence\b", "Fence"),
            (r"\bmiter\s*sled\b", "Miter Sled"),
            (r"\bstock\s*feeder\b", "Stock Feeder"),
            (r"\bdust\s*extractor\b", "Dust Extractor"),
            (r"\bgrinding\s*wheel\b", "Grinding Wheel"),
            (r"\bcut\s*(?:and|n)\s*grind\s*disc\b", "Cut and Grind Disc"),
            (r"\bcut\s*off\s*disc\b|\bcut-off\s*disc\b", "Cut-Off Disc"),
            (r"\bstikit\s*film\b|\bstikit\b", "Stikit Film Disc"),
            (r"\bsanding\s*belt\b", "Sanding Belt"),
            (r"\bsanding\s*sponge\b", "Sanding Sponge"),
            (r"\bsanding\s*disc\b", "Sanding Disc"),
            (r"\babrasive\s*disc\b", "Abrasive Disc"),
            (r"\babrasive\s*mesh\b", "Abrasive Mesh Strip"),
            (r"\bcombo\s*kit\b|\bdrill\s*/\s*impact\b|\bimpact\s*/\s*drill\b", "Combo Kit"),
            (r"\bdishwasher\b", "Dishwasher"),
            (r"\btape\b", "Tape")
        ]
        for t_regex, t_name in type_patterns:
            if re.search(t_regex, desc_lower):
                product_type = t_name
                break

        # Brand-specific defaults if product type not matched directly
        if not product_type:
            if brand in ["HIOLIT", "Mirka"]:
                product_type = "Abrasive Disc"
            elif brand == "Abranet":
                size_test = cls.normalize_dimensions(None, desc)
                product_type = "Abrasive Mesh Strip" if size_test and "x" in size_test else "Abrasive Disc"

        # 4. Size extraction
        size = cls.normalize_dimensions(None, desc)

        # 5. Quantity extraction
        quantity = cls.extract_quantity(desc, None)

        if mpn or brand or product_type or size or quantity is not None:
            info = ProductInfo(
                manufacturer_part_number=mpn,
                brand=brand,
                product_type=product_type,
                size=size,
                quantity=quantity
            )
            conf, status = cls.compute_confidence_and_status(info, desc)
            info.confidence = conf
            info.understanding_status = status
            return info

        return None

    @classmethod
    def normalize_batch_consistency(
        cls,
        extracted_batch: List[Tuple[ProductInfo, str]]
    ) -> List[Tuple[ProductInfo, str]]:
        """
        Batch-level product type consistency check.
        Groups items by product series/family (e.g. '3M 775L Stikit Film') and propagates
        the most descriptive candidate product_type across the family.
        """
        family_to_type: Dict[str, str] = {}

        for info, raw_desc in extracted_batch:
            clean_desc = raw_desc.lower().strip()
            ptype = clean_string_value(info.product_type)

            if ptype and len(ptype) > 4 and ptype.lower() != "disc":
                words = clean_desc.split()
                if len(words) >= 3:
                    family_key = " ".join(words[:3])
                    if family_key not in family_to_type or len(ptype) > len(family_to_type[family_key]):
                        family_to_type[family_key] = ptype

        result = []
        for info, raw_desc in extracted_batch:
            info_clean = cls.sanitize_attributes(info, raw_desc)
            clean_desc = raw_desc.lower().strip()
            words = clean_desc.split()

            if len(words) >= 3:
                family_key = " ".join(words[:3])
                if family_key in family_to_type:
                    canonical_ptype = family_to_type[family_key]
                    current_ptype = info_clean.product_type
                    if current_ptype is None or current_ptype.lower() in ["disc", "abrasive disc"]:
                        info_clean.product_type = canonical_ptype

            conf, status = cls.compute_confidence_and_status(info_clean, raw_desc)
            info_clean.confidence = conf
            info_clean.understanding_status = status

            result.append((info_clean, raw_desc))

        return result

    @classmethod
    def compute_confidence_and_status(cls, info: ProductInfo, raw_desc: str) -> Tuple[float, str]:
        """
        Calculates evidence-based confidence score (0.0 to 1.0) and assigns processing status:
        - success: Core identity extracted (MPN present + 1 other field, OR Brand + Product Type, OR 2+ core fields)
        - partial: Exactly 1 attribute extracted (e.g., MPN only or Brand only)
        - failed: 0 attributes extracted (all fields None)
        """
        if not raw_desc or not raw_desc.strip():
            return 0.0, "failed"

        present_fields = []
        if info.manufacturer_part_number:
            present_fields.append("manufacturer_part_number")
        if info.brand:
            present_fields.append("brand")
        if info.product_type:
            present_fields.append("product_type")
        if info.size:
            present_fields.append("size")
        if info.quantity is not None:
            present_fields.append("quantity")

        num_present = len(present_fields)

        score = 0.0
        if info.manufacturer_part_number:
            score += 0.35
        if info.brand:
            score += 0.25
        if info.product_type:
            score += 0.25
        if info.size:
            score += 0.10
        if info.quantity is not None:
            score += 0.05

        conf = round(min(max(score, 0.0), 1.0), 2)

        if num_present == 0:
            status = "failed"
        elif (info.manufacturer_part_number and info.product_type) or (info.brand and info.product_type) or num_present >= 4:
            status = "success"
        else:
            status = "partial"

        return conf, status
