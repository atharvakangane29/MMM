import pandas as pd
import numpy as np
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, lit, when, row_number 
import warnings
warnings.filterwarnings("ignore")

def reserialise_df(df):
    """
    Returns a dataframe with new serial number to avoid discontinuity in original serial number.
    """
    
    w = Window.orderBy("serial_no")
    df = df.withColumn("new_serial_no", row_number().over(w))
    cols = ["new_serial_no"] + [c for c in df.columns if c != "new_serial_no"]
    df = df.select(cols)
    return df