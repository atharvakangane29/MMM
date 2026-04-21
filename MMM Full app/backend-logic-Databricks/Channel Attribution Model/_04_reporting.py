import re
import pandas as pd
from datetime import datetime
from pyspark.sql.functions import lit, col

def create_master_table(spark, target_catalog, target_schema):

    master_table = f"{target_catalog}.{target_schema}.channel_attribution_master_test"

    spark.sql(f"""
                    CREATE TABLE IF NOT EXISTS {master_table} (
                        run_product STRING,
                        run_segment STRING,
                        run_level STRING,
                        run_start DATE,
                        run_end DATE,
                        run_timestamp STRING,

                        Product STRING,
                        Channel STRING,

                        Attribution_Pct_High_Performer DOUBLE,
                        Attribution_Pct_Moderate_Performer DOUBLE,
                        Attribution_Pct_Average_Performer DOUBLE,
                        Attribution_Pct_Low_Performer DOUBLE,
                        Attribution_Pct_Near_Sleeping DOUBLE,
                        Attribution_Pct_Sleeping DOUBLE,
                        Attribution_Pct_Unresponsive DOUBLE,
                        Attribution_Pct_All_HCPs DOUBLE,
                        Attribution_Pct_does_not_writes DOUBLE,
                        Attribution_Pct_writes DOUBLE,
                        -- Attribution_Pct_less_than_6 DOUBLE,
                        -- Attribution_Pct_more_than_6 DOUBLE,
                        Attribution_Pct_0_2_Years DOUBLE,
                        Attribution_Pct_2_10_Years DOUBLE,
                        Attribution_Pct_10_plus_Years DOUBLE,


                        no_of_hcp_High_Performer BIGINT,
                        no_of_hcp_Moderate_Performer BIGINT,
                        no_of_hcp_Average_Performer BIGINT,
                        no_of_hcp_Low_Performer BIGINT,
                        no_of_hcp_Near_Sleeping BIGINT,
                        no_of_hcp_Sleeping BIGINT,
                        no_of_hcp_Unresponsive BIGINT,
                        no_of_hcp_All_HCPs BIGINT,
                        no_of_hcp_does_not_writes BIGINT,
                        no_of_hcp_writes BIGINT,
                        -- no_of_hcp_less_than_6 BIGINT,
                        -- no_of_hcp_more_than_6 BIGINT,
                        no_of_hcp_0_2_Years BIGINT,
                        no_of_hcp_2_10_Years BIGINT,
                        no_of_hcp_10_plus_Years BIGINT,


                        total_touchpoints_High_Performer BIGINT,
                        total_touchpoints_Moderate_Performer BIGINT,
                        total_touchpoints_Average_Performer BIGINT,
                        total_touchpoints_Low_Performer BIGINT,
                        total_touchpoints_Near_Sleeping BIGINT,
                        total_touchpoints_Sleeping BIGINT,
                        total_touchpoints_Unresponsive BIGINT,
                        total_touchpoints_All_HCPs BIGINT,
                        total_touchpoints_does_not_writes BIGINT,
                        total_touchpoints_writes BIGINT,
                        -- total_touchpoints_less_than_6 BIGINT,
                        -- total_touchpoints_more_than_6 BIGINT,
                        total_touchpoints_0_2_Years BIGINT,
                        total_touchpoints_2_10_Years BIGINT,
                        total_touchpoints_10_plus_Years BIGINT,


                        no_of_prescribers_High_Performer BIGINT,
                        no_of_prescribers_Moderate_Performer BIGINT,
                        no_of_prescribers_Average_Performer BIGINT,
                        no_of_prescribers_Low_Performer BIGINT,
                        no_of_prescribers_Near_Sleeping BIGINT,
                        no_of_prescribers_Sleeping BIGINT,
                        no_of_prescribers_Unresponsive BIGINT,
                        no_of_prescribers_All_HCPs BIGINT,
                        no_of_prescribers_does_not_writes BIGINT,
                        no_of_prescribers_writes BIGINT,
                        -- no_of_prescribers_less_than_6 BIGINT,
                        -- no_of_prescribers_more_than_6 BIGINT,
                        no_of_prescribers_0_2_Years BIGINT,
                        no_of_prescribers_2_10_Years BIGINT,
                        no_of_prescribers_10_plus_Years BIGINT,


                        total_touchpoints_to_prescribers_High_Performer BIGINT,
                        total_touchpoints_to_prescribers_Moderate_Performer BIGINT,
                        total_touchpoints_to_prescribers_Average_Performer BIGINT,
                        total_touchpoints_to_prescribers_Low_Performer BIGINT,
                        total_touchpoints_to_prescribers_Near_Sleeping BIGINT,
                        total_touchpoints_to_prescribers_Sleeping BIGINT,
                        total_touchpoints_to_prescribers_Unresponsive BIGINT,
                        total_touchpoints_to_prescribers_All_HCPs BIGINT,
                        total_touchpoints_to_prescribers_does_not_writes BIGINT,
                        total_touchpoints_to_prescribers_writes BIGINT,
                        -- total_touchpoints_to_prescribers_less_than_6 BIGINT,
                        -- total_touchpoints_to_prescribers_more_than_6 BIGINT
                        total_touchpoints_to_prescribers_0_2_Years BIGINT,
                        total_touchpoints_to_prescribers_2_10_Years BIGINT,
                        total_touchpoints_to_prescribers_10_plus_Years BIGINT

                    )
                    USING DELTA
                    """)

    print(f"✔ Master table created (empty) at {master_table}")


def save_final_output(spark, final_out, products_to_run, col_to_use, level_to_run, start, end, target_catalog, target_schema):
    
    if final_out is None:
        print("No results generated to save.")
        return

    # ---------- FIXED MASTER TABLE ----------
    master_table = f"{target_catalog}.{target_schema}.channel_attribution_master_test"

    if not spark.catalog.tableExists(master_table):
        create_master_table(spark, target_catalog, target_schema)

    # ============================================================
    #  ADD METADATA COLUMNS (with readable labels)
    # ============================================================
    segment_map = {
                        "clustername": "Cluster Level",
                        "lob": "LOB: 0-2 Years vs 2-10 Years vs 10+ Years",
                        "competitor_drug_3": "Writes Direct Competitor vs Does Not Writes Direct Competitor",
                        "competitor_drug_all": "Writes Competitor vs Does Not Writes Competitor (ALL)"
                    }

    level_map = {
                    "channel_5": "Channel Level",
                    "channel_6": "Team Level",
                    "det_touchpoint": "Touchpoint Level"
                }

    final_out["run_product"]    =  ", ".join(products_to_run) 
    final_out["run_segment"]    =  segment_map.get(col_to_use, "All HCPs")
    final_out["run_level"]      =  level_map.get(level_to_run, level_to_run)
    final_out["run_start"]      = start
    final_out["run_end"]        = end

    final_out["run_start"]      =  pd.to_datetime(final_out["run_start"]).dt.date  
    final_out["run_end"]        =  pd.to_datetime(final_out["run_end"]).dt.date
    final_out["run_timestamp"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ============================================================
    #  CLEAN COLUMN NAMES FOR SPARK
    # ============================================================
    final_out_clean = final_out.copy()
    cleaned_cols = []
    for c in final_out_clean.columns:
        clean = c.replace(" %", "_Pct").replace(" ", "_")
        clean = re.sub(r"[^\w]", "", clean)
        cleaned_cols.append(clean)

    final_out_clean.columns = cleaned_cols

    new_df = spark.createDataFrame(final_out_clean)

    # ============================================================
    #  DATATYPE MATCHING
    # ============================================================

    COUNT_PREFIXES = [
        "no_of_hcp_",
        "total_touchpoints_",
        "no_of_prescribers_",
        "total_touchpoints_to_prescribers_"
    ]

    for c in new_df.columns:
        if any(c.startswith(p) for p in COUNT_PREFIXES):
            new_df = new_df.withColumn(c, col(c).cast("long"))
        elif c.startswith("Attribution_Pct_"):
            new_df = new_df.withColumn(c, col(c).cast("double"))

    # ============================================================
    #  IF EXISTS → LOAD MASTER TABLE AND ALIGN SCHEMAS
    # ============================================================
    
    master_df = spark.table(master_table)
    master_cols = set(master_df.columns)
    new_cols = set(new_df.columns)

    for missing_col in master_cols - new_cols:
        new_df = new_df.withColumn(missing_col, lit(None))

    new_df = new_df.select(master_df.columns)

    # ============================================================
    #  APPEND NEW ROWS WITH SCHEMA MERGE ENABLED
    # ============================================================
    new_df.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable(master_table)

    print(f"\nSUCCESS: Rows appended to master table: {master_table}")
