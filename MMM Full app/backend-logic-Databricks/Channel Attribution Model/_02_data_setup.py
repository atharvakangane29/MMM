# setup.py

# import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp
from helpers._00_data_prep import build_hcp_long_for_model

def initialize_spark_and_data(start, end, comp_table):
    """
    Initializes Spark, loads the main table and cutoff definitions.
    Returns:
        Tuple: (spark, df_spark, cutoffs)
    """
    
    ################################################################# CREATING A SPARK SESSION AND LOADING THE MAIN TABLE ###########################################################################################

    spark = SparkSession.builder.getOrCreate()

    df_spark = build_hcp_long_for_model(start, end, comp_table)   

    # ADDING METADATA COLUMN TO THE LONGITUDINAL DATA PREPARED AND WILL SAVE IT AS A TABLE AFTER JOINING WITH JOURNEYS TABLE
    
    df_final = (
                    df_spark
                    .withColumn("run_start_date", lit(start))
                    .withColumn("run_end_date", lit(end))
                    .withColumn("run_timestamp", current_timestamp())
                )

    #################################################################### READING THE ALREADY CREATED 'CUTOFFS' DATAFRAME #############################################################################################
  
    cutoffs = spark.table("`coe-consultant-catalog`.channel_attribution.cutoffs")

    return spark, df_spark, cutoffs, df_final





