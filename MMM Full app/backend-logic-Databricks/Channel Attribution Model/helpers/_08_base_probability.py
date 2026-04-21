import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")

def get_paths_and_base_metrics(df_selected_final):
    """
    Returns a tuple containing 4 itmes:
        1. paths_list_new (list of lists) 
            List containing all the paths in standard Python list(for further processing).
        2. total_conversions (Float)
            Total number of journeys with Conversion in final dataset.
        3. total_nulls (Float)
            Total number of journeys with No Conversion in the final dataset. 
        4. base_conversion_rate (Float)
            Base conversion rate calculated using total conversions and total journeys.
    """

    total_conversions = 0
    total_nulls = 0
    total_jounreys = len(df_selected_final)

    paths_list_new = []

    for path in df_selected_final['journey_path']:
        paths_list_new.append(path)
        if 'Null' in path:
            total_nulls += 1
        if 'Conversion' in path:
            total_conversions += 1

    base_conversion_rate = (total_conversions / len(paths_list_new) if len(paths_list_new) > 0 else 0)

    return paths_list_new, total_conversions, total_nulls, base_conversion_rate


def get_unique_channels(paths_list):
    """
    Returns a sorted list of unique channel names (strings) found in the provided 'paths_list'.
    """

    unique_channels = sorted(list(set(channel for path in paths_list for channel in path)))
    return unique_channels