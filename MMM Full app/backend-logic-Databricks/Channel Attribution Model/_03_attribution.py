
import pandas as pd
import numpy as np
from pyspark.sql.functions import col, countDistinct, lit, max as spark_max, min as spark_min, current_timestamp
from collections import defaultdict

from helpers._01_scenario_filter import product_cluster_filter
from helpers._02_data_filter import nothing_after_last_referral
from helpers._03_cutoff import apply_cutoff_logic
from helpers._04_reorder import reserialise_df
from helpers._06_impression_conversion import assign_impression_conversion
from helpers._05_preprocess import (assign_only_referral_HCPs_flag, assign_first_tp_referral_flag, 
                                          assign_consecutive_referrals_flag, assign_consecutive_marketing_flag, assign_consecutive_marketing_flag_cutoff)
from helpers._07_journey import assign_journey_number, assign_journey_number_cutoff, assign_journey_number_last_ref, create_journey_path
from helpers._08_base_probability import get_paths_and_base_metrics, get_unique_channels
from helpers._09_transition_probability import get_transition_and_state_counts, create_transition_matrix
from helpers._10_removal_effect import calculate_removal_effects
from helpers._11_result import display_final_removal_effects

import warnings
warnings.filterwarnings("ignore")

def calculate_touchpoint_summary(df, selected_channel_col):
    """ 
    Helper function to calculate touchpoint summaries mid-pipeline. 
    Returns a dictionary with two pandas DataFrames:
        1. 'All_HCPs': touchpoints to all HCPs
        2. 'Prescribers': touchpoints to prescribers only
    """
    
    toucpoints_to_all_HCPs = (
                                df.filter(col(selected_channel_col) != "Conversion")
                                .groupBy(selected_channel_col)
                                    .agg(
                                            countDistinct('hcp_id').alias('no_of_hcp'),
                                            countDistinct('event_id').alias('total_touchpoints')
                                        )
                                        .orderBy(col("total_touchpoints").desc())
                            )

    prescribers_df = (
                        df.filter(col("event_channel") == "Referral")
                        .select("hcp_id")
                        .distinct()
                    )

    toucpoints_to_prescribers = (
                                    df.join(prescribers_df, on="hcp_id", how="inner")
                                    .filter(col(selected_channel_col) != "Conversion")
                                    .groupBy(selected_channel_col)
                                        .agg(
                                                countDistinct("hcp_id").alias("no_of_prescribers"),
                                                countDistinct("event_id").alias("total_touchpoints_to_prescribers")
                                            )
                                )
    
    final_spark_df = (
                        toucpoints_to_all_HCPs
                        .join(
                                toucpoints_to_prescribers,
                                on=selected_channel_col,
                                how="left"
                            )
                        .fillna(0) 
                        .withColumnRenamed(selected_channel_col, "Channel")
                    )

    final_df = final_spark_df.toPandas()
    final_df = final_df.sort_values("total_touchpoints", ascending=False)

    return final_df

def data_prep(spark, df_spark, cutoffs, prod, col_to_use, value_in_col, selected_channel_col, df_final, start, end):
    """ 
    Function to run the entire pipeline data preparation. 
    """

    column_used = "ALL_HCPs" if col_to_use is None else value_in_col

    # 1. INITIAL FILTERING
    qc_summary, df_filtered = product_cluster_filter(df_spark, prod, col_to_use, value_in_col)

    print(f"\n--- Initial Product and Segment Filtering for {column_used}_{prod}_{selected_channel_col} ---")
    print(qc_summary)
    print(f'Combination is : {column_used}_{prod}_{selected_channel_col}')

    # 2. FLAG, REMOVE AND STORE SEPERATELY EVERYTHING AFTER LAST REFERRAL
    df_filtered = nothing_after_last_referral(df_filtered, prod)
    flag_col_ref = f"exclusion_flag_after_last_marketing_{prod}"
    df_removed_due_to_after_last_ref = df_filtered.filter(col(flag_col_ref) == 1)
    df_filtered = df_filtered.filter(col(flag_col_ref) == 0)
    print(f"Removed {df_removed_due_to_after_last_ref.count()} rows after last referral.")

    # 3. APPLY CUTOFF LOGIC
    df_filtered = apply_cutoff_logic(cutoffs, df_filtered, prod)
    flag_col_cutoff = f"exclusion_flag_{prod}"
    df_removed_due_to_cutoff = df_filtered.filter(col(flag_col_cutoff) == 1)
    df_filtered = df_filtered.filter(col(flag_col_cutoff) == 0)
    print(f"Removed {df_removed_due_to_cutoff.count()} rows due to cutoff logic.")

    # 4. RESERIALISE
    df_serialised = reserialise_df(df_filtered)

    # 5. REMOVE 'ONLY REFERRAL' HCPS
    df_with_flags = assign_only_referral_HCPs_flag(df_serialised)
    removed_df = df_with_flags.filter(col("hcp_with_only_ref_flag") == 1)
    df_clean = df_with_flags.filter(col("hcp_with_only_ref_flag") == 0)
    print(f"Removed {removed_df.count()} rows from HCPs with only referrals.")

    # 6. REMOVE 'FIRST TP REFERRAL'
    df_with_flags = assign_first_tp_referral_flag(df_clean)
    removed_df = df_with_flags.filter(col("first_tp_referral_flag") == 1)
    df_clean = df_with_flags.filter(col("first_tp_referral_flag") == 0)
    print(f"Removed {removed_df.count()} rows where referral was the first touchpoint.")

    # 7. REMOVE CONSECUTIVE REFERRALS
    df_with_flags = assign_consecutive_referrals_flag(df_clean)
    removed_df = df_with_flags.filter(col("consecutive_referral") == 1)
    df_clean = df_with_flags.filter(col("consecutive_referral") == 0)
    print(f"Removed {removed_df.count()} consecutive referral rows.")

    # 8. ASSIGN INTERACTION
    df_with_interaction = assign_impression_conversion(df_clean, prod, selected_channel_col)

    # 9. CALCULATE TOUCHPOINT SUMMARY
    touchpoints_summary_run = calculate_touchpoint_summary(df_with_interaction, selected_channel_col)

    # 10. REMOVE CONSECUTIVE MARKETING
    df_with_flags = assign_consecutive_marketing_flag(df_with_interaction, selected_channel_col)
    removed_df = df_with_flags.filter(col("consecutive_marketing") == 1)

    df_removed_due_to_cutoff = assign_consecutive_marketing_flag_cutoff(df_removed_due_to_cutoff, selected_channel_col, prod)
    df_removed_due_to_cutoff = df_removed_due_to_cutoff.where(col('consecutive_marketing') == 0)

    df_removed_due_to_after_last_ref = assign_consecutive_marketing_flag(df_removed_due_to_after_last_ref, selected_channel_col)
    df_removed_due_to_after_last_ref = df_removed_due_to_after_last_ref.where(col('consecutive_marketing') == 0)

    # 8. ASSIGN INTERACTION TO EVENTS CAUSING NULL JOURNEYS FOR PRESCRIBING HCPs
    df_removed_due_to_cutoff_IMP_CONV = assign_impression_conversion(df_removed_due_to_cutoff, prod, selected_channel_col)
    df_removed_due_to_after_last_ref_IMP_CONV = assign_impression_conversion(df_removed_due_to_after_last_ref, prod, selected_channel_col)

    df_with_interaction = df_with_flags.filter(col("consecutive_marketing") == 0)
    print(f"Removed {removed_df.count()} consecutive marketing rows.")

    # 11. CREATE JOURNEYS 
    df_with_journey_number = assign_journey_number(df_with_interaction, selected_channel_col)
    df_cutoff_excl_journey_no = assign_journey_number_cutoff(df_removed_due_to_cutoff_IMP_CONV, selected_channel_col, prod)
    df_after_last_ref_journey_no = assign_journey_number_last_ref(df_removed_due_to_after_last_ref_IMP_CONV, selected_channel_col)

    # COMBINING ALL THE JOURNEYS
    df_final_all_journeys = (
                                df_with_journey_number
                                .unionAll(df_cutoff_excl_journey_no)
                                .unionAll(df_after_last_ref_journey_no)
                            )

############################################################################################################################################################
    
    # METADATA COLUMNS
    run_product = prod 
    run_segment = column_used     
    run_level = selected_channel_col
    run_start = start
    run_end = end
    run_ts = current_timestamp()

    # PRINT LONGITUDINAL TABLE WITH JOUNREY ID FOR CORRESPONDING EVENTS
    df1 = df_final.alias("df1")
    df2 = df_final_all_journeys.alias("df2")

    df_final = df1.join(df2, col("df1.event_id") == col("df2.event_id"), "left").select(col('df1.*'), col('df2.journey_id'))

    target_catalog = "`coe-consultant-catalog`"
    target_schema = "channel_attribution"
    table_name = f"{target_catalog}.{target_schema}.hcp_longitudinal_data_test"

    spark.sql(f"""
                    CREATE TABLE IF NOT EXISTS {table_name}
                    USING DELTA
                """)
    
    df_final = (
                    df_final
                    # .withColumn("run_id", lit(run_id))
                    .withColumn("run_product", lit(run_product))
                    .withColumn("run_segment", lit(run_segment))
                    .withColumn("run_level", lit(run_level))
                    # .withColumn("run_timestamp", run_ts)
                )

    # Save in append mode to a constant delta table
    df_final.write.mode("append").option("mergeSchema", "true").saveAsTable(table_name)

    print(f"Successfully appended HCP Longitudinal Data with journeys to table: {table_name}")

###############################################################################################################################################################

    # PRINT JOURNEYS DATAFRAME AS A TABLE
    df_with_journey_path = create_journey_path(df_final_all_journeys, selected_channel_col)

    table_name_2 = f"{target_catalog}.{target_schema}.hcp_journeys_test"

    spark.sql(f"""
                    CREATE TABLE IF NOT EXISTS {table_name_2}
                    USING DELTA
                """)
    
    df_with_journey_path = (
                                df_with_journey_path
                                # .withColumn("run_id", lit(run_id))
                                .withColumn("run_product", lit(run_product))
                                .withColumn("run_segment", lit(run_segment))
                                .withColumn("run_level", lit(run_level))
                                .withColumn("run_start_date", lit(run_start))
                                .withColumn("run_end_date", lit(run_end))
                                .withColumn("run_timestamp", run_ts)
                            )
    
    df_with_journey_path.select("journey_id", "journey_path", "run_product", "run_segment", "run_level",
    "run_start_date", "run_end_date", "run_timestamp").write.mode("append").option("mergeSchema", "true").saveAsTable(table_name_2)

    print(f"Successfully appended new journeys to: {table_name_2}")

################################################################################################################################################################
    
    df_selected_final = df_with_journey_path.select("journey_id", "journey_path").toPandas()

    return df_selected_final, touchpoints_summary_run

def markov_calculations(df_selected_final, prod, value_in_col, touchpoints_summary_run, col_to_use):
    """
    Function which calculates the actual Markov Chain calculations for each product.
    """

    paths_list, total_conversions, total_nulls, base_conversion_rate = get_paths_and_base_metrics(df_selected_final)
    
    print(f"Total Conversions: {total_conversions}")
    print(f"Total Nulls: {total_nulls}")
    print(f"Total Journeys: {len(paths_list)}")

    unique_channels = get_unique_channels(paths_list)
    transition_counts, state_totals = get_transition_and_state_counts(paths_list)
    transition_matrix = create_transition_matrix(unique_channels, transition_counts, state_totals)
    removal_effects = calculate_removal_effects(transition_matrix, base_conversion_rate)
    final_attribution = display_final_removal_effects(removal_effects, prod, value_in_col)
    
    final_attribution['Channel'] = final_attribution['Channel'].astype(str)
    touchpoints_summary_run['Channel'] = touchpoints_summary_run['Channel'].astype(str)

    final_df = pd.merge(final_attribution, touchpoints_summary_run, on='Channel', how='inner')

    # RENAME ALL COLUMNS EXCEPT 'CHANNEL'
    if col_to_use is None:
        final_df = final_df.rename(columns={c: f"{c}_All_HCPs" for c in final_df.columns if c != "Channel"})
    else:
        final_df = final_df.rename(columns={c: f"{c}_{value_in_col}" for c in final_df.columns if c != "Channel"})

    return final_df