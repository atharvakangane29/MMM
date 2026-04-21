import pandas as pd
import numpy as np
from pyspark.sql import Window
from pyspark.sql.functions import col, when, sum as spark_sum, lag, lead

import warnings
warnings.filterwarnings("ignore")

# ASSIGNS FLAG TO REOCRDS OF HCPs WITH ONLY REFERRAL
def assign_only_referral_HCPs_flag(df):                                            
    """
    Returns a Dataframe with flag for HCPs with only referrals and no marketing.
    """
   
    w = Window.partitionBy("hcp_id").rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)

    marketing_per_hcp = df.withColumn("marketing_count", spark_sum(when(col("event_channel") != "Referral", 1).otherwise(0)).over(w))
    df_with_flag = marketing_per_hcp.withColumn("hcp_with_only_ref_flag", when(col("marketing_count") == 0, 1).otherwise(0))

    return df_with_flag

# ASSIGNS FLAG TO REFERRALS OCCURING AT START OF HCP'S JOURNEY
def assign_first_tp_referral_flag(df):
    """
    Returns a Dataframe with flag for Referral records (one/multiple) that were before any marketing for an HCP.
    """

    # CHECKS IF MAREKTING WAS BEFORE
    w = Window.partitionBy("hcp_id").orderBy("new_serial_no")
    df = df.withColumn("marketing_seen", spark_sum(when(col("event_channel") != "Referral", 1).otherwise(0)).over(w))      

    # FLAGGING REFERRALS IF THEY WERE BEFORE MARKETING
    df = df.withColumn("first_tp_referral_flag", when((col("event_channel") == "Referral") & (col("marketing_seen") == 0), 1).otherwise(0))

    df = df.drop("marketing_seen")

    return df

# ASSIGNS FLAG IF REFERRALS ARE CONSECUTIVE
def assign_consecutive_referrals_flag(df):                                          
    """
    Returns a Dataframe with flag for Referral records if they were consecutive without any marketing event between them, except the first one.
    """

    w = Window.partitionBy("hcp_id").orderBy("new_serial_no")

    df = df.withColumn("prev_channel", lag("event_channel", 1).over(w))
    df = df.withColumn("consecutive_referral", when((col("event_channel") == "Referral") & (col("prev_channel") == "Referral"), 1).otherwise(0))

    return df

# ASSIGNS FLAG TO MAREKTING EVENTS IF CONSECUTIVE AND SAME 
def assign_consecutive_marketing_flag(df, selected_channel_col):                   
    """
    Returns a Dataframe with flag for marekting records if they were consecutive and same.
    """
    w = Window.partitionBy("hcp_id").orderBy("serial_no")

    df = df.withColumn("next_touchpoint_val", lead(selected_channel_col, 1).over(w))
    df = df.withColumn("consecutive_marketing", when((col("event_channel") != 'Referral') & (col(selected_channel_col) == col("next_touchpoint_val")), 1).otherwise(0))

    return df

# ASSIGNS FLAG TO MAREKTING EVENTS IF CONSECUTIVE AND SAME FOR ROWS REMOVED DUE TO CUTOFF RULE
def assign_consecutive_marketing_flag_cutoff(df, selected_channel_col, product_name):                   
    """
    Returns a Dataframe with flag for marekting records if they were consecutive and same.
    """
    partition_col = f"next_referral_date_{product_name}"

    w = Window.partitionBy("hcp_id", partition_col).orderBy("serial_no")

    df = df.withColumn("next_touchpoint_val", lead(selected_channel_col, 1).over(w))
    df = df.withColumn("consecutive_marketing", when((col("event_channel") != 'Referral') & (col(selected_channel_col) == col("next_touchpoint_val")), 1).otherwise(0))

    return df