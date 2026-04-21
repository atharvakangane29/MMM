import pandas as pd
import numpy as np
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, lit, when, row_number, sum as spark_sum, lag, concat, collect_list, array, element_at, struct, expr, dense_rank

import warnings
warnings.filterwarnings("ignore")


def assign_journey_number(df, attribution_level_col):
    """
    Returns a DataFrame with a new column 'journey_number' that assigns a unique journey number to each row.
    """
  
    w = Window.partitionBy("hcp_id").orderBy("serial_no")

    # CUMMULATIVE COUNTS TO COUNT THE JOURNEY GROUP IT BELONGS TOO
    conversion_block = spark_sum(when(col(attribution_level_col) == 'Conversion', 1).otherwise(0)).over(w)   
    df = df.withColumn("conversion_block", conversion_block)

    # FIRST SHIFTED NULL VALUE REPLACED BY 0 , +1 TO START JOURNEY NO. FROM 1 INSTEAD OF 0
    journey_number_col = lag("conversion_block", 1, 0).over(w) + 1                          
    df = df.withColumn("journey_number", journey_number_col).drop("conversion_block")

    # SELECTING REQUIRED COLUMNS ONLY
    selected_columns = ["serial_no", "event_id", "hcp_id", "journey_number", "event_date", attribution_level_col]
    df_selected = df.select(*selected_columns)

    # JOURNEY ID CREATION
    df = df_selected.withColumn("journey_id", concat(col("hcp_id"), lit("_"), col("journey_number")))       

    return df

################################################ JOURNEY NUMBER FUNCTIONS - FOR REMOVED EVENTS ###################################################################################################

def assign_journey_number_cutoff(df, attribution_level_col, product_name):
    """
    Assign journey_number based on unique (hcp_id, next_referral_date_{product_name}) combos.
    All rows with same hcp_id AND same next_referral_date_{product_name} get the same journey_number.
    Journey numbers start at 1 and increment per unique partition value per hcp_id.
    """
    
    partition_col = f"next_referral_date_{product_name}"

    # DENSE RANK HERE WILL GIVE SAME NUMBER TO SAME NEXT REFERRAL DATE ROWS FOR EACH HCP
    w = Window.partitionBy("hcp_id").orderBy(col(partition_col))

    df2 = (df.withColumn("journey_number", dense_rank().over(w)))

    selected_columns = ["serial_no", "event_id", "hcp_id", "journey_number", "event_date", attribution_level_col]
    df_selected = df2.select(*selected_columns)

    df_final = df_selected.withColumn("journey_id", concat(col("hcp_id"), lit("_rc_"), col("journey_number").cast("string")))

    return df_final

def assign_journey_number_last_ref(df, attribution_level_col):
    """
    Assigns journey_number = 1 for all rows, because these events occur only AFTER the last referral.
    """

    df = df.withColumn("journey_number", lit(1))

    selected_columns = ["serial_no", "event_id", "hcp_id", "journey_number", "event_date", attribution_level_col]
    df_selected = df.select(*selected_columns)

    df_final = df_selected.withColumn("journey_id", concat(col("hcp_id"), lit("_rl_"), col("journey_number")))

    return df_final


############################################################################################################################################################################################


def create_journey_path(df, attribution_level_col):
    """
    Returns a DataFrame with two columns Jounrey ID and Journey Path, which is a list of events in the journey. 
    """

    # ADD AN ORDER INDEX WITHIN EACH JOURNEY
    w = Window.partitionBy("journey_id").orderBy("serial_no")
    df = df.withColumn("order_idx", row_number().over(w))
    
    # COLLECT BOTH INDEX AND EVENT, THEN SORT
    df = (df.groupBy("journey_id").agg(collect_list(struct(col("order_idx"), col(attribution_level_col))).alias("events")))

    # SORT BY INDEX AND EXTRACT ONLY THE EVENT NAMES
    df = df.withColumn("journey_path", expr("transform(array_sort(events), x -> x." + attribution_level_col + ")"))

    # ADD "START" AT THE BEGINNING
    df = df.withColumn("journey_path", concat(array(lit("Start")), col("journey_path")))

    # APPEND "NULL" IF LAST ELEMENT IS NOT CONVERSION
    df = df.withColumn(
                        "journey_path",
                        when(
                                element_at(col("journey_path"), -1) != "Conversion", concat(col("journey_path"), array(lit("Null")))
                            ).otherwise(col("journey_path"))
                        )
    
    return df

