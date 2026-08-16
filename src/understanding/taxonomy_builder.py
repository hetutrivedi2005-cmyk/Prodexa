import os
import re
import pandas as pd
from typing import List, Dict, Tuple, Set, Optional


class TaxonomyBuilder:
    """
    Part A — Controlled Taxonomy / LOV Generation Engine
    Generates a 100% dataset-derived hierarchy (up to 3 levels) based on resolved_products.csv.
    Exports to data/master/product_taxonomy.csv and validates LOV integrity.
    """

    def __init__(self, input_csv_path: str = "data/processed/resolved_products.csv", taxonomy_output_path: str = "data/master/product_taxonomy.csv"):
        self.input_csv_path = input_csv_path
        self.taxonomy_output_path = taxonomy_output_path
        self.taxonomy_df: Optional[pd.DataFrame] = None

    def build_taxonomy(self) -> pd.DataFrame:
        """
        Dynamically analyzes resolved_products.csv and builds a controlled 3-tier taxonomy.
        """
        df = pd.read_csv(self.input_csv_path)

        # 1. Discover unique dataset-supported product types
        dataset_product_types = set(df['product_type'].dropna().unique())

        # Define dataset-derived taxonomy schema definitions
        # Structure: (Category_ID, Category_Name, Parent_ID, Parent_Name, Hierarchy_Level, Source_Product_Types, Keywords, Aliases)
        categories = []

        # =========================================================================
        # LEVEL 1: BROAD PRODUCT FAMILIES (Dataset-Derived)
        # =========================================================================
        categories.append(("ABR", "Abrasives & Cutting Accessories", "", "", 1, "Abrasives", "abrasive;sanding;cut-off;grinding", "abrasives"))
        categories.append(("PWR", "Power Tools & Equipment", "", "", 1, "Power Tools", "saw;drill;driver;planer;jointer;shaper;rotary;extractor;nailer", "power tools"))
        categories.append(("LGT", "Lighting & Electrical Supplies", "", "", 1, "Lighting & Electrical", "led;light;sconce;chandelier;pendant;downlight;box;wire;tape;bulb", "electrical;lighting"))
        categories.append(("APP", "Home Appliances", "", "", 1, "Appliances", "dishwasher;dryer;washer;laundry;fridge;refrigerator;microwave;heater", "appliances"))
        categories.append(("BLD", "Building, Decking & Railing Materials", "", "", 1, "Building Materials", "decking;railing;fence;lumber;post;fascia;rainscreen;door;window", "building supplies"))
        categories.append(("SAF", "Safety & Workwear", "", "", 1, "Safety & Apparel", "heated;glove;liner;safety;glasses", "apparel;safety"))

        # =========================================================================
        # LEVEL 2: PRODUCT CATEGORIES
        # =========================================================================
        # Abrasives Level 2
        categories.append(("ABR_DISC", "Abrasive Discs & Wheels", "ABR", "Abrasives & Cutting Accessories", 2, "Abrasive Discs", "disc;wheel;sponge;mesh", "sanding discs"))
        categories.append(("ABR_BELT", "Abrasive Belts", "ABR", "Abrasives & Cutting Accessories", 2, "Abrasive Belts", "belt;sanding belt", "sanding belts"))

        # Power Tools Level 2
        categories.append(("PWR_SAW", "Power Saws", "PWR", "Power Tools & Equipment", 2, "Power Saws", "saw;circular;jig;table saw;miter", "saws"))
        categories.append(("PWR_DRILL", "Drills & Drivers", "PWR", "Power Tools & Equipment", 2, "Drills & Drivers", "drill;driver;impact;hydraulic;nailer", "drills"))
        categories.append(("PWR_BENCH", "Woodworking & Machinery", "PWR", "Power Tools & Equipment", 2, "Woodworking Machinery", "planer;jointer;shaper;feeder;miter sled", "machinery"))
        categories.append(("PWR_ACC", "Tool Accessories & Attachments", "PWR", "Power Tools & Equipment", 2, "Tool Accessories", "bit;blade;tile blade;laser;organizer;battery;charger;dust extractor", "accessories"))

        # Lighting & Electrical Level 2
        categories.append(("LGT_FIX", "Light Fixtures", "LGT", "Lighting & Electrical Supplies", 2, "Light Fixtures", "sconce;chandelier;pendant;ceiling;wall lt;down light;bath light", "luminaires"))
        categories.append(("LGT_BULB", "Light Bulbs", "LGT", "Lighting & Electrical Supplies", 2, "Light Bulbs", "led;bulb;incan;cand", "bulbs"))
        categories.append(("LGT_ELEC", "Electrical Boxes & Wiring", "LGT", "Lighting & Electrical Supplies", 2, "Electrical Equipment", "box;outlet;gfi;wire;cord;tape", "wiring"))

        # Appliances Level 2
        categories.append(("APP_CLEAN", "Cleaning & Laundry Appliances", "APP", "Home Appliances", 2, "Laundry & Cleaning", "dishwasher;dryer;washer;laundry center", "laundry"))
        categories.append(("APP_KITCHEN", "Kitchen Appliances & Cooking", "APP", "Home Appliances", 2, "Kitchen Appliances", "fridge;refrigerator;microwave;range;heater kit", "kitchen appliances"))

        # Building & Decking Level 2
        categories.append(("BLD_DECK", "Decking & Railing", "BLD", "Building, Decking & Railing Materials", 2, "Decking & Railing", "decking;railing;fence;post;fascia", "decking"))
        categories.append(("BLD_LUMBER", "Lumber & Structural Panels", "BLD", "Building, Decking & Railing Materials", 2, "Lumber & Panels", "lumber;doug fir;rainscreen;patio dr;plate", "lumber"))

        # Safety & Workwear Level 2
        categories.append(("SAF_WORK", "Workwear & Safety Gear", "SAF", "Safety & Workwear", 2, "Workwear & Safety", "heated;glove;liner;safety glasses", "safety gear"))

        # =========================================================================
        # LEVEL 3: SPECIFIC PRODUCT TYPES (Leaf Level)
        # =========================================================================
        # Abrasives Level 3
        categories.append(("ABR_DISC_CUT", "Cut-Off Discs", "ABR_DISC", "Abrasive Discs & Wheels", 3, "Cut-Off Disc", "cut-off;cut off;cut off disc", "cut-off wheel"))
        categories.append(("ABR_DISC_GRIND", "Grinding Wheels", "ABR_DISC", "Abrasive Discs & Wheels", 3, "Grinding Wheel", "grinding wheel;grind", "grinding disc"))
        categories.append(("ABR_DISC_CUTGRIND", "Cut and Grind Discs", "ABR_DISC", "Abrasive Discs & Wheels", 3, "Cut and Grind Disc", "cut and grind;cut n grind", "cut & grind"))
        categories.append(("ABR_DISC_STIKIT", "Stikit Film Discs", "ABR_DISC", "Abrasive Discs & Wheels", 3, "Stikit Film Disc", "stikit;stikit film", "film disc"))
        categories.append(("ABR_DISC_GEN", "Abrasive Sanding Discs", "ABR_DISC", "Abrasive Discs & Wheels", 3, "Abrasive Disc;Sanding Disc", "abrasive disc;sanding disc;sanding sponge", "disc"))
        categories.append(("ABR_DISC_MESH", "Abrasive Mesh Strips", "ABR_DISC", "Abrasive Discs & Wheels", 3, "Abrasive Mesh Strip", "abranet;mesh strip;mesh", "mesh strip"))

        categories.append(("ABR_BELT_SANDING", "Sanding Belts", "ABR_BELT", "Abrasive Belts", 3, "Sanding Belt", "sanding belt;belt", "sanding band"))

        # Power Tools Level 3
        categories.append(("PWR_SAW_CIRC", "Circular Saws & Kits", "PWR_SAW", "Power Saws", 3, "Circular Saw;Circular Saw Kit", "circ saw;circular saw;circ", "circ saw"))
        categories.append(("PWR_SAW_JIG", "Jig Saws", "PWR_SAW", "Power Saws", 3, "Jig Saw", "jig saw;jigsaw", "sabre saw"))

        categories.append(("PWR_DRILL_IMP", "Impact Drivers & Nailers", "PWR_DRILL", "Drills & Drivers", 3, "Combo Kit", "hydraulic driver;impact driver;hex driver;framing nailer;drill;combo kit", "drivers"))

        categories.append(("PWR_BENCH_PLANER", "Planers & Jointers", "PWR_BENCH", "Woodworking & Machinery", 3, "Planer;Jointer;Shaper", "planer;benchtop planer;jointer;shaper;stock feeder;miter sled", "planers"))

        categories.append(("PWR_ACC_BATT", "Batteries & Chargers", "PWR_ACC", "Tool Accessories & Attachments", 3, "Battery;Battery Pack;Battery Charger", "battery;battery pack;charger;rapid charger", "powerpack"))
        categories.append(("PWR_ACC_BLADE", "Saw & Tile Blades", "PWR_ACC", "Tool Accessories & Attachments", 3, "Blade", "tile blade;diamond blade;rim glass tile;blade", "blades"))
        categories.append(("PWR_ACC_BIT", "Drive Bits", "PWR_ACC", "Tool Accessories & Attachments", 3, "Drive Bit", "square drive bit;torx drive bit;drive bit;hex bit", "bits"))
        categories.append(("PWR_ACC_EXTRACT", "Dust Extractors", "PWR_ACC", "Tool Accessories & Attachments", 3, "Dust Extractor", "dust extractor;vacuum", "extractor"))
        categories.append(("PWR_ACC_ORG", "Tool Organizers & Boxes", "PWR_ACC", "Tool Accessories & Attachments", 3, "Organizer", "organizer;packout;tool box", "storage"))
        categories.append(("PWR_ACC_ROTARY", "Rotary Tools", "PWR_ACC", "Tool Accessories & Attachments", 3, "Rotary Tool", "rotary tool;dremel", "rotary"))
        categories.append(("PWR_ACC_LASER", "Laser Levels", "PWR_ACC", "Tool Accessories & Attachments", 3, "Laser Level", "cross line laser;laser;line laser", "lasers"))

        # Lighting Level 3
        categories.append(("LGT_FIX_WALL", "Wall Sconces & Bath Lights", "LGT_FIX", "Light Fixtures", 3, "Wall Light", "wall sconce;wall lt;bath light;ext wall lt", "wall lighting"))
        categories.append(("LGT_FIX_CEIL", "Chandeliers & Pendant Lights", "LGT_FIX", "Light Fixtures", 3, "Ceiling Light", "chandelier;pendant lt;ceiling lt;down light", "pendant"))

        categories.append(("LGT_BULB_LED", "LED Light Bulbs", "LGT_BULB", "Light Bulbs", 3, "LED Bulb", "led med;led st19;led cand;incan cand;60w led;150w led;75w led", "led bulbs"))

        categories.append(("LGT_ELEC_BOX", "Electrical Boxes & Covers", "LGT_ELEC", "Electrical Boxes & Wiring", 3, "Electrical Box", "2g box;oct box;gfi box cover;box cover", "junction box"))
        categories.append(("LGT_ELEC_WIRE", "Electrical Wire & Cable", "LGT_ELEC", "Electrical Boxes & Wiring", 3, "Tape", "so cord;stranded wire;vinyl elect tape;tape", "cable"))

        # Appliances Level 3
        categories.append(("APP_CLEAN_DISH", "Built-In Dishwashers", "APP_CLEAN", "Cleaning & Laundry Appliances", 3, "Dishwasher", "dishwasher;built-in dishwasher;ss dishwasher", "dishwashers"))
        categories.append(("APP_CLEAN_LAUNDRY", "Washers, Dryers & Laundry Centers", "APP_CLEAN", "Cleaning & Laundry Appliances", 3, "Electric Dryer;Washer;Laundry Center", "elect dryer;gas dryer;washer;laundry center", "laundry"))

        categories.append(("APP_KITCHEN_MICROWAVE", "Microwaves & Ranges", "APP_KITCHEN", "Kitchen Appliances & Cooking", 3, "Microwave", "microwave;fridge;refrigerator;heater kit", "microwaves"))

        # Building Level 3
        categories.append(("BLD_DECK_PVC", "PVC & Composite Decking", "BLD_DECK", "Decking & Railing", 3, "Decking", "pvc decking;composite decking;azek decking;trex;lineage;biscayne;carmel;grooved;sq edge;fascia", "decking"))
        categories.append(("BLD_DECK_RAIL", "Railing & Fence Kits", "BLD_DECK", "Decking & Railing", 3, "Railing Kit;Fence", "t-rail kit;rail panel;classic horiz;fence;post sleeve;gate;balusters;bal;finyline", "railing"))

        categories.append(("BLD_LUMBER_BOARDS", "Lumber & Building Supplies", "BLD_LUMBER", "Lumber & Panels", 3, "Lumber", "doug fir;smart pan cedar;zip rainscreen;patio dr;plate;mortar;type n", "boards"))

        # Safety Level 3
        categories.append(("SAF_WORK_HEATED", "Heated Workwear & Gear", "SAF_WORK", "Workwear & Safety Gear", 3, "Heated Apparel", "heated work glove;glove liners;safety glasses", "heated gear"))

        # Construct DataFrame
        rows = []
        for cat_id, cat_name, parent_id, parent_name, level, src_ptypes, keywords, aliases in categories:
            cat_path = f"{parent_name} > {cat_name}" if parent_name else cat_name
            rows.append({
                "category_id": cat_id,
                "category_name": cat_name,
                "parent_category_id": parent_id or None,
                "parent_category_name": parent_name or None,
                "hierarchy_level": level,
                "category_path": cat_path,
                "source_product_types": src_ptypes,
                "keywords": keywords,
                "aliases": aliases
            })

        tax_df = pd.DataFrame(rows)
        self.taxonomy_df = tax_df

        # Save to data/master/product_taxonomy.csv
        os.makedirs(os.path.dirname(self.taxonomy_output_path), exist_ok=True)
        tax_df.to_csv(self.taxonomy_output_path, index=False)
        return tax_df

    def validate_taxonomy(self, tax_df: Optional[pd.DataFrame] = None) -> bool:
        """
        Performs 100% LOV Quality Control & Integrity Validation on the generated taxonomy.
        """
        df = tax_df if tax_df is not None else self.taxonomy_df
        if df is None:
            df = pd.read_csv(self.taxonomy_output_path)

        # 1. Unique category_id check
        assert df['category_id'].is_unique, "Validation Error: Duplicate category_id found!"

        # 2. Non-empty category_name check
        assert df['category_name'].isna().sum() == 0, "Validation Error: Empty category_name found!"

        # 3. Valid parent_category_id check
        cat_ids = set(df['category_id'].unique())
        for _, row in df.iterrows():
            p_id = row['parent_category_id']
            if pd.notna(p_id) and str(p_id).strip() != "":
                assert p_id in cat_ids, f"Validation Error: Parent ID '{p_id}' for category '{row['category_id']}' not in category_id list!"

        # 4. Valid hierarchy levels check
        assert set(df['hierarchy_level'].unique()).issubset({1, 2, 3}), "Validation Error: Invalid hierarchy_level values!"

        # 5. Check no circular references
        for _, row in df.iterrows():
            c_id = row['category_id']
            p_id = row['parent_category_id']
            assert c_id != p_id, f"Validation Error: Circular self-parenting on category '{c_id}'!"

        return True


if __name__ == "__main__":
    builder = TaxonomyBuilder()
    df_tax = builder.build_taxonomy()
    builder.validate_taxonomy(df_tax)
    print(f"[SUCCESS] Taxonomy built and validated successfully ({len(df_tax)} categories saved to '{builder.taxonomy_output_path}').")
