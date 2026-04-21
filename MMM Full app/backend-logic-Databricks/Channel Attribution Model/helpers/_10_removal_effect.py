import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")

def calculate_removal_effects(transition_matrix, base_conversion_rate):
    """
    Calculates the impact of removing each marketing channel on the overall conversion rate 
    based on the provided transition probability matrix.

    Returns a Dictionary,
        1. Key : Channel Name
        2. Value : Removal Effect (Float)
    """

    removal_effects = {}
    channels_to_remove = [ch for ch in transition_matrix.index if ch not in ['Start', 'Null', 'Conversion']]

    for channel in channels_to_remove:

        modified_matrix = transition_matrix.drop(channel, axis=0, errors='ignore').drop(channel, axis=1, errors='ignore')

        row_sums = modified_matrix.sum(axis=1)
        if 'Null' not in modified_matrix.columns:
            modified_matrix['Null'] = 0.0
        modified_matrix['Null'] += (1.0 - row_sums).fillna(0.0)

        if 'Null' in modified_matrix.index:
            modified_matrix.loc['Null', 'Null'] = 1.0
        if 'Conversion' in modified_matrix.index:
            modified_matrix.loc['Conversion', 'Conversion'] = 1.0

        non_absorbing_states = [state for state in modified_matrix.columns if state not in ['Null', 'Conversion']]

        if len(non_absorbing_states) == 0:
            new_conversion_rate = 0.0
        else:
            Q = modified_matrix.loc[non_absorbing_states, non_absorbing_states]
            R = modified_matrix.loc[non_absorbing_states, ['Null', 'Conversion']]

            try:
                identity = np.identity(len(Q))
                fundamental_matrix = np.linalg.inv(identity - Q.values)
                absorption_probs = pd.DataFrame(np.dot(fundamental_matrix, R.values), index=R.index, columns=R.columns)
                new_conversion_rate = absorption_probs.get('Conversion', pd.Series(0.0)).get('Start', 0.0)
            except np.linalg.LinAlgError:
                new_conversion_rate = 0.0

        removal_effect = 1.0 - (new_conversion_rate / base_conversion_rate) if base_conversion_rate > 0 else 0.0
        removal_effects[channel] = removal_effect

    return removal_effects