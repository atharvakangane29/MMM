import pandas as pd
import numpy as np
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, lit, when, min as spark_min, datediff

import warnings
warnings.filterwarnings("ignore")

def apply_cutoff_logic(cutoffs, df, product_name):
    """
    Returns a Datframe with the flag if the record would be excluded by cutoff rule.
    """
    # FOR DYNAMIC COLUMN NAMING
    first_ref_date_col = f"first_referral_date_{product_name}"                                            
    next_ref_date_col = f"next_referral_date_{product_name}"
    days_until_next_ref_col = f"days_until_next_referral_{product_name}"
    exclusion_flag_col = f"exclusion_flag_{product_name}"

    w = Window.partitionBy("hcp_id")
    df_with_first_ref = df.withColumn(first_ref_date_col, spark_min(when(col("event_channel") == "Referral", col("event_date"))).over(w))

    # CALCULATES NEXT NEAREST REFERRAL DATE
    w = Window.partitionBy("hcp_id").orderBy("serial_no").rowsBetween(1, Window.unboundedFollowing)        
    
    df_with_next_ref = df_with_first_ref.withColumn(
                                                    next_ref_date_col,
                                                    spark_min(when(col("event_channel") == "Referral", col("event_date"))).over(w)
                                                ).withColumn(
                                                    days_until_next_ref_col,
                                                    when(col("event_channel") == "Referral", 0)
                                                    .otherwise(datediff(col(next_ref_date_col), col("event_date")))
                                                )

    df_with_cutoff = df_with_next_ref.join(cutoffs, on=["event_channel", "event_type"], how='left')

    exclusion_condition = (
                                (
                                    (col(first_ref_date_col).isNotNull() & (col("event_date") <= col(first_ref_date_col))) 
                                    |
                                    (col(first_ref_date_col).isNull()) 
                                )
                                |
                                (
                                    (col("days_cutoff").isNotNull() & (col(days_until_next_ref_col) <= col("days_cutoff"))) 
                                    |
                                    (col("event_channel") == "Referral") 
                                    |
                                    (col(days_until_next_ref_col).isNull())
                                )
                            )

    df_flagged = df_with_cutoff.withColumn(exclusion_flag_col, when(exclusion_condition, lit(0)).otherwise(lit(1))).orderBy("serial_no")

    return df_flagged

  
