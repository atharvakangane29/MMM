import pandas as pd
import numpy as np
from pyspark.sql.functions import col, when 

import warnings
warnings.filterwarnings("ignore")

def assign_impression_conversion(df, product_name, selected_channel_col):
    """
    Returns a dataframe in which each event/record is marked as either 'Conversion' or 'Impression'.
    """

    # COLUMN ADDED TO MAKE REFERRAL AS CONVERSION AND ALL OTHER AS IMPRESSIONS
    interaction_col = f'Interaction_{product_name}'
    df = df.withColumn(interaction_col, when(col('event_channel') == 'Referral', 'Conversion').otherwise('Impression'))

    # UPDATED ATTROBTUION LEVEL COLUMN WHERE EVENT_CHANNEL = 'Referral'  (NEEDS TO BE USED FURTHER)
    df = df.withColumn(selected_channel_col, when(col('event_channel') == 'Referral', 'Conversion').otherwise(col(selected_channel_col)))

    return df