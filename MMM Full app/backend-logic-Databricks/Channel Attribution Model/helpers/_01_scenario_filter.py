import pandas as pd
import numpy as np
from pyspark.sql.functions import col, upper, lit, when
import warnings
warnings.filterwarnings("ignore")


def product_cluster_filter(df_spark, prod, col_to_use, value_in_col):
    """
    Filters the input Spark DataFrame based on the specified product and HCP cluster given by the user as input. 
    Returns a tuple containing two items:
        1. qc_summary (PySpark DataFrame)
            A summary table showing before-and-after counts of total records, unique HCPs, total referrals, and referral-writing HCPs.
        2. filtered_df (PySpark DataFrame) 
            The filtered Spark DataFrame containing only the records relevant to the specified product and cluster.
    """
    
    if prod and prod.strip() != '' and prod.upper() != 'TREPROSTINIL':
        filtered_df = df_spark.filter(
                                        (
                                            (col("event_channel") == "Referral") & (upper(col("product_name")) == prod.upper())
                                        )
                                        |
                                        (
                                            (col("event_channel") != "Referral") &
                                            (
                                                upper(col("product_name")).like(f"%{prod.upper()}%") |
                                                upper(col("product_name")).like("%TREPROSTINIL%")
                                            )
                                        )
                                    )

    else:
       filtered_df = df_spark
    
    total_records_before = df_spark.count()
    total_hcp_before = df_spark.select('hcp_id').distinct().count()
    total_referrals_before = df_spark.filter(col("event_channel") == "Referral").count()
    hcp_with_referral_before = df_spark.where(col("event_channel") == "Referral").select('hcp_id').distinct().count()

    ######################################################## FILTERED AT HCP SEGMENT LEVEL ########################################################################

    if col_to_use == 'clustername':
        col_to_choose = f'{prod}_{col_to_use}'
        filtered_df = filtered_df.where(col(col_to_choose) == value_in_col)

    elif col_to_use == 'lob':
        col_to_choose = f'{prod}_{col_to_use}'
        filtered_df = filtered_df.where(col(col_to_choose) == value_in_col)   
         
    elif col_to_use == 'competitor_drug_3':
        col_to_choose = f'{prod}_{col_to_use}'
        filtered_df = filtered_df.where(col(col_to_choose) == value_in_col)

    ######################################################## NEW ADDED - 13 JAN ###################################################################################

    elif col_to_use == 'competitor_drug_all':
        col_to_choose = f'{prod}_{col_to_use}'
        filtered_df = filtered_df.where(col(col_to_choose) == value_in_col)
    
    ###############################################################################################################################################################

    else:
        filtered_df = filtered_df

    total_records_after = filtered_df.count()
    total_hcp_after = filtered_df.select('hcp_id').distinct().count()
    total_referrals_after = filtered_df.filter(col("event_channel") == "Referral").count()
    hcp_with_referral_after = filtered_df.where(col('event_channel') == "Referral").select('hcp_id').distinct().count()
    
    qc_summary = pd.DataFrame(
                                {
                                    "Metric": ["Total Records", "Total HCPs", "Total Referrals", "Referral Writting HCPs"],
                                    "In Original Dataframe": [total_records_before, total_hcp_before, total_referrals_before, hcp_with_referral_before],
                                    "In Filtered Dataframe": [total_records_after, total_hcp_after, total_referrals_after, hcp_with_referral_after]
                                }
                            )
    
    return qc_summary, filtered_df
