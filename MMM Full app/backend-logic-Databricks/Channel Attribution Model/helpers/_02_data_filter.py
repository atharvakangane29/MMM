import pandas as pd
import numpy as np
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, upper, countDistinct, lit, when, min as spark_min, max as spark_max, datediff, row_number, sum, lag,lead, concat, concat_ws, collect_list, array, element_at, struct, expr

import warnings
warnings.filterwarnings("ignore")

def nothing_after_last_referral(df, product_name):
    """
    Returns a dataframe with flag stating if the event has happened after the last referral of the HCP.
    """

    last_ref_date_col = f"last_referral_date_{product_name}"
    exclusion_flag_col = f"exclusion_flag_after_last_marketing_{product_name}"

    w = Window.partitionBy("hcp_id")
    df_with_last_ref = df.withColumn(last_ref_date_col, spark_max(when(col("event_channel") == "Referral", col("event_date"))).over(w))

    df_flagged = df_with_last_ref.withColumn(exclusion_flag_col, when((col("event_date") > col(last_ref_date_col)) & (col("event_channel") != "Referral"), 1) .otherwise(0)).orderBy("serial_no")

    return df_flagged