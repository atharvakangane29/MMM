from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils
from _01_input import get_user_inputs

import warnings
import pandas as pd
from pyspark.sql import Row

from _02_data_setup import initialize_spark_and_data
from _03_attribution import data_prep, markov_calculations
from _04_reporting import save_final_output

def main(comp_table):
 
    spark = SparkSession.builder.getOrCreate()
    dbutils = DBUtils(spark)
 
    # Get runtime inputs
    start, end, products_to_run, levels_to_run, col_to_use= get_user_inputs()
 
    # -------------------------------------------------
    # PIPELINE LOGIC STARTS HERE
    # -------------------------------------------------
    print("Pipeline started")
    print(f"start = {start}")
    print(f"end = {end}")
    print(f"products_to_run = {products_to_run}")
    print(f"levels_to_run = {levels_to_run}")
    print(f"col_to_use = {col_to_use}")

    spark, df_spark, cutoffs, df_final = initialize_spark_and_data(start, end, comp_table)

    final_out = None  

    TARGET_CATALOG = "`coe-consultant-catalog`"
    TARGET_SCHEMA = "results"

    # ============================================================
    #  PREDEFINED ORDER MAPS
    # ============================================================
    cluster_order = {
        "HIGH PERFORMER": 1, "MODERATE PERFORMER": 2, "AVERAGE PERFORMER": 3,
        "LOW PERFORMER": 4, "NEAR SLEEPING": 5, "SLEEPING": 6, "UNRESPONSIVE": 7
    }

    lob_order = {"0_2_YEARS": 1, "2_10_YEARS": 2, "10_PLUS_YEARS":3}

    competitor_order = {"WRITES": 1, "DOES_NOT_WRITES": 2}

    # ============================================================
    #  PROCESS EACH PRODUCT
    # ============================================================
    for prod in products_to_run:

        # Build column name: e.g., TYVASO_clustername
        col_name = f"{prod}_{col_to_use}" if col_to_use else None

        # ------------------------------------------------------------
        # GET DISTINCT SEGMENT VALUES (CLUSTERS / LOB / COMPETITOR)
        # ------------------------------------------------------------
        if col_name is None:
            segment_rows = [None]  # No segmentation to apply

        else:
            raw_vals = df_spark.select(col_name).na.drop().distinct().collect()
            values = [str(r[0]) for r in raw_vals]
            upper_vals = {v.upper() for v in values}

            # Ordered categories based on known mapping
            if upper_vals == set(cluster_order.keys()):
                ordered = sorted(values, key=lambda v: cluster_order[v.upper()])

            elif upper_vals == set(lob_order.keys()):
                ordered = sorted(values, key=lambda v: lob_order[v.upper()])

            elif upper_vals.issubset(set(competitor_order.keys())):
                ordered = sorted(values, key=lambda v: competitor_order[v.upper()])

            else:
                ordered = sorted(values)

            segment_rows = [Row(**{col_name: v}) for v in ordered]

        # ============================================================
        #  PROCESS EACH SEGMENT WITHIN THE PRODUCT
        # ============================================================
        base_df = None  # pandas df for this product

        for seg_row in segment_rows:

            segment_val = None if seg_row is None else seg_row[col_name]

            # Prepare data for this product × segment
            df_selected, touch_summary = data_prep(spark, df_spark, cutoffs, prod, col_to_use, segment_val, levels_to_run, df_final, start, end)

            # Perform attribution logic
            result_df = markov_calculations(df_selected, prod, segment_val, touch_summary, col_to_use)

            # ----------------------------------------------
            # MERGE results across segments
            # ----------------------------------------------
            if base_df is None:
                first_attr_col = (f"Attribution %_All_HCPs"
                                  if col_to_use is None
                                  else f"Attribution %_{segment_val}")
                base_df = result_df

            else:
                base_df = pd.merge(base_df, result_df, on="Channel", how="outer")

            # Sort by first attribution metric if available
            if first_attr_col in base_df.columns:
                base_df = base_df.sort_values(first_attr_col, ascending=False).reset_index(drop=True)

            # Reorder columns: Channel → Attribution cols → Remaining cols
            attrib_cols = [c for c in base_df.columns if "Attribution %" in c]
            other_cols = [c for c in base_df.columns if c not in attrib_cols and c != "Channel"]
            base_df = base_df[["Channel"] + attrib_cols + other_cols]

        # ============================================================
        #  AFTER PROCESSING ALL SEGMENTS → ADD PRODUCT COLUMN
        # ============================================================
        if base_df is not None:
            base_df.insert(0, "Product", prod)

            if final_out is None:
                final_out = base_df
            else:
                final_out = pd.concat([final_out, base_df], ignore_index=True)

    # ============================================================
    #  PRINT STATUS
    # ============================================================
    print("\n" + "="*50)
    print("FINAL ATTRIBUTION OUTPUT GENERATED")
    print("="*50)

    print(final_out)

    spark.createDataFrame(final_out).display()

    # ============================================================
    #  SAVE RESULT INTO MASTER TABLE
    # ============================================================
    save_final_output(
        spark, final_out, products_to_run, col_to_use,
        levels_to_run, start, end, TARGET_CATALOG, TARGET_SCHEMA
    )

if __name__ == "__main__":

    comp_table = dbutils.jobs.taskValues.get(
                                                taskKey="claims_notebook",  # TASK NAME in DATABRICKS JOB -- REPLACE HERE
                                                key="comp_table",
                                                default=None
                                            )
    main(comp_table)
