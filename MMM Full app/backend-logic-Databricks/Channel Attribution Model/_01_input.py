import argparse

def get_user_inputs():
 
    # 1. Setup Argument Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_date", required=True)
    parser.add_argument("--end_date", required=True)
    parser.add_argument("--product", required=False, default="TREPROSTINIL")
    parser.add_argument("--level", required=True)
    parser.add_argument("--segment", required=True)
 
    # 2. Parse arguments
    args = parser.parse_args()
    start = args.start_date
    end = args.end_date
 
    # -------------------------------------------------
    # Product Logic
    # -------------------------------------------------

    all_products = ["TYVASO", "REMODULIN", "ORENITRAM", "TREPROSTINIL"]
    product_input_raw = (args.product or "").strip().upper()
 
    if product_input_raw == "ALL":
        products_to_run = all_products
        product_status = "ALL PRODUCTS SELECTED"

    elif product_input_raw in all_products:
        products_to_run = [product_input_raw]
        product_status = "SINGLE SELECTION"

    else:
        raise ValueError(f"Invalid product: {product_input_raw}")
 
    # -------------------------------------------------
    # Level Logic
    # -------------------------------------------------

    level_mapping = {
        "touchpoint level": "det_touchpoint",
        "channel level": "channel_5",
        "team level": "channel_6"
    }
 
    level_input_raw = args.level
    level_input_clean = level_input_raw.strip().lower()
 
    if level_input_clean not in level_mapping:
        raise ValueError(f"Invalid level '{level_input_raw}'")
 
    levels_to_run = level_mapping[level_input_clean]
 
    # -------------------------------------------------
    # Segment Logic
    # -------------------------------------------------

    segment_input = str(args.segment)

    col_mapping = {
        "1": "All HCPs (No Segmentation)",
        "2": "clustername (All Clusters)",
        "3": "lob (LOB Buckets)",
        "4": "competitor_drug_3 (Direct Competitors)",
        "5": "competitor_drug_all (All Competitors)"
    }

    col_to_use = {
        "1": None,
        "2": "clustername",
        "3": "lob",
        "4": "competitor_drug_3",
        "5": "competitor_drug_all"
    }.get(segment_input)

    if segment_input not in col_mapping:
        raise ValueError(f"Invalid segment '{segment_input}'. Choose from 1–5.")
 
    # ---------------------------------------------------------
    # QC STEP: PRINT REPORT TO DRIVER LOGS
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("              RUNTIME PARAMETERS QC REPORT")
    print("=" * 60)

    print(f"1. DATE RANGE:")
    print(f"   - Start:  {start}")
    print(f"   - End:    {end}")

    print("-" * 60)

    print(f"2. PRODUCT SELECTION:")
    print(f"   - Raw Input:      '{product_input_raw}'")
    print(f"   - Interpretation: {product_status}")
    print(f"   - FINAL LIST:     {products_to_run}")

    print("-" * 60)

    print(f"3. LEVEL SELECTION:")
    print(f"   - Raw Input:      '{level_input_raw}'")
    print(f"   - Mapped To Code: '{levels_to_run}'")

    print("-" * 60)

    print(f"4. SEGMENTATION:")
    print(f"   - Segment ID:     {segment_input}")
    print(f"   - Column Used:    {col_mapping.get(segment_input)}")

    print("=" * 60 + "\n")

    # ---------------------------------------------------------
    return start, end, products_to_run, levels_to_run, col_to_use

