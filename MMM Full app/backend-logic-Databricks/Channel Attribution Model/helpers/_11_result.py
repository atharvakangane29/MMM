import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")


def display_final_removal_effects(removal_effects, prod, value_in_col):
    """
    Converts the removal effects dictionary into a sorted Pandas DataFrame with percentage attribution for each marketing channel.
    Returns a Pandas DataFrame with columns: Channel, Attribution.
    """

    value_in_col = value_in_col if value_in_col is not None else 'All HCPs'

    results_df = pd.DataFrame.from_dict(removal_effects, orient='index', columns=['Removal Effect']).fillna(0.0)

    total_effect = results_df['Removal Effect'].sum()
    if total_effect > 0:
        results_df['Attribution %'] = results_df['Removal Effect'] / total_effect 
    else:
        results_df['Attribution %'] = 0.0

    results_df = results_df.sort_values('Attribution %', ascending=False)

    # CAN UNCOMMENT THE BELOW LINE IF YOU WANT FORMATTED OUTPUT IN SQL TABLE (ALSO NEED TO DO THIS THING ABOVE --> results_df['Attribution %'] = 100 * results_df['Removal Effect'] / total_effect)
    # results_df['Attribution %'] = results_df['Attribution %'].round(0).astype(int).astype(str) + '%'

    results_df = results_df.reset_index().rename(columns={'index': 'Channel'})

    print(f"\n REMOVAL EFFECTS FOR PRODUCT : {value_in_col} of {prod}")

    return results_df[['Channel', 'Attribution %']]
