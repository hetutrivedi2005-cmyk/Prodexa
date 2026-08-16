import os
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set


class AttributeSchemaBuilder:
    """
    Part 1 — Attribute Schema Builder (Semantically Precise)
    Derives category-specific attribute definitions directly from dataset evidence in classified_products.csv.
    Exports to data/master/category_attributes.csv.
    """

    def __init__(self, classified_csv_path: str = "data/processed/classified_products.csv", output_csv_path: str = "data/master/category_attributes.csv"):
        self.classified_csv_path = classified_csv_path
        self.output_csv_path = output_csv_path
        self.attributes_df: Optional[pd.DataFrame] = None

    def build_schema(self) -> pd.DataFrame:
        df = pd.read_csv(self.classified_csv_path)
        rows = []

        def add_attr(cat_id: str, cat_name: str, attr_id: str, attr_name: str, attr_type: str, req: bool, uom: str, allowed: str, keywords: str, aliases: str):
            rows.append({
                "category_id": cat_id,
                "category_name": cat_name,
                "attribute_id": attr_id,
                "attribute_name": attr_name,
                "attribute_type": attr_type,
                "is_required": req,
                "unit_of_measure": uom,
                "allowed_values": allowed,
                "extraction_keywords": keywords,
                "aliases": aliases
            })

        # =========================================================================
        # CATEGORY-SPECIFIC SCHEMAS (Semantically Precise)
        # =========================================================================

        # 1. Sanding Belts & Mesh Strips (ABR_BELT_SANDING, ABR_DISC_MESH) -> dimensions, grit, pack_quantity
        for cid in ["ABR_BELT_SANDING", "ABR_DISC_MESH"]:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Belts & Strips"
            add_attr(cid, c_name, "grit", "Grit Rating", "enum", False, "Grit", "P80;P120;P150;P180;P220;P320", "grit;p80;p120;p150;p180;p220;p320", "grit size")
            add_attr(cid, c_name, "dimensions", "Belt/Strip Dimensions", "measurement", False, "in", "", "dimensions;size;x;width;length;1/2 x 18;2.75x30", "belt dimensions")
            add_attr(cid, c_name, "pack_quantity", "Pack Quantity", "integer", False, "pcs", "", "pc;pcs;box;pack;6pc;50pc", "package count")

        # 2. Circular Discs & Cut-Off Wheels (ABR_DISC_CUT, ABR_DISC_STIKIT, ABR_DISC_GEN, ABR_DISC_GRIND, ABR_DISC_CUTGRIND) -> diameter, arbor_size, grit, pack_quantity, target_material
        disc_cat_ids = ["ABR_DISC_CUT", "ABR_DISC_STIKIT", "ABR_DISC_GEN", "ABR_DISC_GRIND", "ABR_DISC_CUTGRIND", "ABR_DISC", "ABR"]
        for cid in disc_cat_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Abrasive Discs"
            add_attr(cid, c_name, "grit", "Grit Rating", "enum", False, "Grit", "P80;P120;P150;P180;P220;P320", "grit;p80;p120;p150;p180;p220;p320", "grit size")
            add_attr(cid, c_name, "diameter", "Disc Diameter", "measurement", False, "in", "4 in;5 in;6 in;7 in;9 in;12 in;14 in", "diameter;disc;inch;in;4\";5\";7\";9\";12\";14\"", "disc diameter")
            add_attr(cid, c_name, "arbor_size", "Arbor Hole Size", "measurement", False, "in", "7/8 in;5/8 in;20mm;1 in", "arbor;hole;bore;7/8;5/8;20mm", "arbor size")
            add_attr(cid, c_name, "pack_quantity", "Pack Quantity", "integer", False, "pcs", "", "pc;pcs;box;pack;disc/box", "package count")
            add_attr(cid, c_name, "target_material", "Target Material", "string", False, "", "Metal;Steel Demon;Speed Demon;Tile;General Purpose", "metal;steel;tile;masonry", "application material")

        # 3. Lighting Categories (LGT_BULB_LED, LGT_FIX_WALL, LGT_FIX_CEIL, LGT_BULB, LGT_FIX, LGT)
        lighting_cat_ids = ["LGT_BULB_LED", "LGT_FIX_WALL", "LGT_FIX_CEIL", "LGT_BULB", "LGT_FIX", "LGT"]
        for cid in lighting_cat_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Lighting"
            add_attr(cid, c_name, "wattage", "Wattage", "measurement", False, "W", "4W;6W;7W;10W;12W;25W;60W;75W;150W", "w;watt;wattage;60w;75w;150w", "power consumption")
            add_attr(cid, c_name, "color_temperature", "Color Temperature", "enum", False, "K", "2700K;3000K;4000K;5000K", "27k;30k;50k;2700k;3000k;5000k", "color temp;cct")
            add_attr(cid, c_name, "color_finish", "Color / Finish", "string", False, "", "Black;Brushed Nickel;White;Architectural Bronze;Distressed Black;Brushed Slate", "black;bk;ni;wh;dbk;bsl", "finish")
            add_attr(cid, c_name, "pack_quantity", "Pack Quantity", "integer", False, "pk", "", "pk;pack;2pk;4pk", "bulb count")

        # 4. Decking & Railing Categories (BLD_DECK_PVC, BLD_DECK_RAIL, BLD_DECK)
        deck_cat_ids = ["BLD_DECK_PVC", "BLD_DECK_RAIL", "BLD_DECK"]
        for cid in deck_cat_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Decking & Railing"
            add_attr(cid, c_name, "length", "Board / Rail Length", "measurement", False, "ft", "6 ft;8 ft;12 ft;16 ft;20 ft", "ft;length;6';8';12';16';20'", "length")
            add_attr(cid, c_name, "width_profile", "Width / Profile Size", "measurement", False, "in", "1x6;4x4;6x6;1x8;1x12", "1x6;4x4;6x6;1x8;1x12", "profile")
            add_attr(cid, c_name, "color", "Color / Tone", "enum", False, "", "Coastline;English Walnut;French White Oak;Slate Gray;White;Black;Charcoal;Clay;Biscayne;Carmel", "coastline;walnut;oak;slate;white;black;charcoal;clay;biscayne;carmel", "color")
            add_attr(cid, c_name, "edge_profile", "Edge Profile", "enum", False, "", "Square Edge;Grooved;Fascia", "sq edge;grooved;fascia", "edge type")
            add_attr(cid, c_name, "material", "Material", "enum", False, "", "PVC;Composite;Aluminum;Vinyl", "pvc;composite;alum;vinyl", "material type")

        # 5. Appliances Categories (APP_CLEAN_LAUNDRY, APP_KITCHEN_MICROWAVE, APP_CLEAN_DISH, APP_CLEAN, APP_KITCHEN, APP)
        appliance_cat_ids = ["APP_CLEAN_LAUNDRY", "APP_KITCHEN_MICROWAVE", "APP_CLEAN_DISH", "APP_CLEAN", "APP_KITCHEN", "APP"]
        for cid in appliance_cat_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Appliances"
            add_attr(cid, c_name, "color_finish", "Color / Finish", "enum", False, "", "White;Black;Stainless Steel;Juniper", "wh;bk;ss;stainless steel;juniper", "appliance color")
            add_attr(cid, c_name, "power_type", "Power Source", "enum", False, "", "Electric;Gas", "elect;electric;gas", "fuel type")
            add_attr(cid, c_name, "display_status", "Display Condition", "enum", False, "", "Display Only;New", "display only;display", "unit condition")

        # 6. Tool Accessories Categories (PWR_ACC_BIT, PWR_ACC_BLADE, PWR_ACC_BATT, PWR_ACC_LASER, PWR_ACC_ORG, PWR_ACC_ROTARY, PWR_ACC_EXTRACT, PWR_ACC)
        tool_acc_ids = ["PWR_ACC_BIT", "PWR_ACC_BLADE", "PWR_ACC_BATT", "PWR_ACC_LASER", "PWR_ACC_ORG", "PWR_ACC_ROTARY", "PWR_ACC_EXTRACT", "PWR_ACC"]
        for cid in tool_acc_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Tool Accessories"
            add_attr(cid, c_name, "drive_size", "Drive Size", "measurement", False, "in", "1/4 in;3/8 in;1/2 in", "1/4;3/8;1/2;hex", "drive size")
            add_attr(cid, c_name, "voltage", "Voltage Rating", "measurement", False, "V", "12V;18V;20V;120V", "12v;18v;20v;120v", "voltage")
            add_attr(cid, c_name, "amp_hour", "Battery Capacity", "measurement", False, "Ah", "8Ah;12Ah", "8ah;12ah;ah", "battery amp hour")
            add_attr(cid, c_name, "piece_count", "Piece Count", "integer", False, "pc", "", "pc;set;pk;pack;6pk;50pc;84pc", "piece count")
            add_attr(cid, c_name, "bit_type", "Bit Drive Type", "enum", False, "", "Phillips;Torx;Square Drive;Hex;Universal Joint", "phillips;torx;square drive;hex;universal joint", "bit geometry")

        # 7. Electrical Wiring Categories (LGT_ELEC_WIRE, LGT_ELEC_BOX, LGT_ELEC)
        wire_cat_ids = ["LGT_ELEC_WIRE", "LGT_ELEC_BOX", "LGT_ELEC"]
        for cid in wire_cat_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Electrical Wiring"
            add_attr(cid, c_name, "length", "Tape / Wire Length", "measurement", False, "ft", "50 ft;60 ft;13 ft;500 ft", "ft;60';13';50';500'", "wire length")
            add_attr(cid, c_name, "width", "Tape Width", "measurement", False, "in", "3/4 in;1.5 in;2 in", "3/4;1.5;2;in", "width")
            add_attr(cid, c_name, "box_gang", "Electrical Box Gang", "enum", False, "", "2G;Octagon", "2g;oct", "gang count")

        # 8. Safety Categories (SAF_WORK_HEATED, SAF_WORK, SAF)
        safety_cat_ids = ["SAF_WORK_HEATED", "SAF_WORK", "SAF"]
        for cid in safety_cat_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Safety & Workwear"
            add_attr(cid, c_name, "color", "Frame / Gear Color", "enum", False, "", "Black;Red;Clear", "black;red;clear", "item color")
            add_attr(cid, c_name, "lense_type", "Lens Technology", "enum", False, "", "Photochromic;Red Lenses;Clear", "photochromic;red lenses;clear", "lens type")

        # 9. Lumber & Structural Panels (BLD_LUMBER_BOARDS, BLD_LUMBER)
        lumber_cat_ids = ["BLD_LUMBER_BOARDS", "BLD_LUMBER"]
        for cid in lumber_cat_ids:
            c_rows = df[df['category_id'] == cid]
            c_name = c_rows['category_name'].iloc[0] if not c_rows.empty else "Lumber & Building Supplies"
            add_attr(cid, c_name, "thickness", "Panel Thickness", "measurement", False, "in", "1/2 in;5/8 in;3/4 in", "1/2;5/8;3/4", "thickness")
            add_attr(cid, c_name, "wood_species", "Wood Species", "enum", False, "", "Doug Fir;Cedar;French White Oak", "doug fir;cedar;white oak", "wood type")
            add_attr(cid, c_name, "mortar_type", "Mortar Grade", "enum", False, "", "Type N", "type n;mortar", "mortar type")

        schema_df = pd.DataFrame(rows)
        self.attributes_df = schema_df

        os.makedirs(os.path.dirname(self.output_csv_path), exist_ok=True)
        schema_df.to_csv(self.output_csv_path, index=False)
        return schema_df

    def validate_schema(self, schema_df: Optional[pd.DataFrame] = None) -> bool:
        df = schema_df if schema_df is not None else self.attributes_df
        if df is None:
            df = pd.read_csv(self.output_csv_path)

        assert df['category_id'].isna().sum() == 0, "Validation Error: Empty category_id!"
        assert df['attribute_id'].isna().sum() == 0, "Validation Error: Empty attribute_id!"
        assert set(df['attribute_type'].unique()).issubset({"string", "integer", "float", "boolean", "enum", "measurement"}), "Validation Error: Unsupported attribute_type!"
        return True


if __name__ == "__main__":
    builder = AttributeSchemaBuilder()
    df_s = builder.build_schema()
    builder.validate_schema(df_s)
    print(f"[SUCCESS] Attribute master built and validated: {len(df_s)} attribute records saved to '{builder.output_csv_path}'.")
