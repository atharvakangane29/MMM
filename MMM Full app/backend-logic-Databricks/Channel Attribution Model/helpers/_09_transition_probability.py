import pandas as pd
import numpy as np
from collections import defaultdict


import warnings
warnings.filterwarnings("ignore")


def get_transition_and_state_counts(paths_list):
    """
    Calculates transition counts and total outgoing transitions for each channel state based on a list of journey paths. Each transition represents a movement from one channel to the next within a path, excluding absorbing states like 'Conversion' and 'Null'.
    Returns a tuple containing two dictionaries:
        1. transition_counts (defaultdict[int])
            A dictionary where each key is a string representing a transition in the format "current_state > next_state" and the value is the number of times that transition occurred across all paths.
        2. state_totals (defaultdict[int]) 
            A dictionary where each key is a channel (origin state) and the value is the total number of outgoing transitions from that channel.
    """

    transition_counts = defaultdict(int)
    state_totals = defaultdict(int)

    for path in paths_list:
        for i in range(len(path) - 1):
            current_state = path[i]
            next_state = path[i + 1]
            if current_state not in ['Conversion', 'Null']:                        
                transition_counts[f"{current_state}>{next_state}"] += 1

    for transition, count in transition_counts.items():
        origin_state = transition.split('>')[0]
        state_totals[origin_state] += count

    return transition_counts, state_totals


def create_transition_matrix(unique_channels, transition_counts, state_totals):
    """
    Builds a transition probability matrix representing the likelihood of moving from one channel (state) to another based on observed transition counts.
    The matrix includes both regular and absorbing states. Probabilities are calculated by dividing each transition count by the total number of outgoing transitions from the origin state.

    Returns a pandas DataFrame representing the transition probability matrix.
    """

    transition_matrix = pd.DataFrame(0.0, index=unique_channels, columns=unique_channels)

    # ABSORBING STATES
    for absorbing_state in ['Conversion', 'Null']:
        if absorbing_state in transition_matrix.index:
            transition_matrix.loc[absorbing_state, absorbing_state] = 1.0

    # FILL PROBABILITIES
    for transition, count in transition_counts.items():
        origin, destination = transition.split('>')
        if origin in transition_matrix.index and destination in transition_matrix.columns:
            total = state_totals[origin]
            if total > 0:
                transition_matrix.at[origin, destination] = count / total

    return transition_matrix