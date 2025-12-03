import collections
from typing import Tuple, List, Optional
from pyeda.inter import *
from collections import deque
import numpy as np

def max_reachable_marking(
    place_ids: List[str], 
    bdd: BinaryDecisionDiagram, 
    c: np.ndarray
) -> Tuple[Optional[List[int]], Optional[int]]:
    """
    Finds a reachable marking M that maximizes the linear objective function c^T * M.
    This function iterates through all satisfying assignments of the BDD representing 
    the reachable set and calculates the objective value for each marking.
    
    Args:
        place_ids: List of place names corresponding to BDD variables.
        bdd: The BDD representing the set of all reachable markings (from Task 3).
        c: A numpy array of integer weights corresponding to place_ids.
        
    Returns:
        Tuple: (best_marking, max_value)
            - best_marking: The marking (List[int]) that yields the maximum value.
            - max_value: The maximum calculated objective value.
            - Returns (None, None) if the reachable set is empty.
    """
    
    # Case 1: The BDD represents an empty set (No reachable markings)
    if bdd.is_zero():
        return None, None

    # Initialize max_val with negative infinity to ensure any valid marking will be greater.
    max_val = -float('inf')
    best_marking = None

    # Iterate through all satisfying assignments (solutions) of the BDD.
    # Note: 'satisfy_all()' returns an iterator of points (dictionaries).
    # A point might be a partial assignment (e.g., {p1: 1, p3: 0}), meaning 
    # unlisted variables (e.g., p2) are "Don't Care" (can be 0 or 1).
    for point in bdd.satisfy_all():
        current_marking = []
        current_val = 0
        
        # Convert BDD variable objects in the 'point' dictionary to strings for easier lookup.
        # Example: {p[0]: 1} -> {'p1': 1} (assuming variables are named correctly)
        point_str_keys = {str(k): v for k, v in point.items()}

        for i, place_name in enumerate(place_ids):
            weight = c[i]
            
            # Check if the variable for this place is explicitly defined in the BDD solution.
            if place_name in point_str_keys:
                # If defined, use the value from the BDD (0 or 1).
                bit = point_str_keys[place_name]
            else:
                # Case 2: Variable is "Don't Care" (not in the point dictionary).
                # Optimization Strategy:
                # - If weight > 0: Choose 1 to maximize the sum.
                # - If weight <= 0: Choose 0 to avoid reducing the sum.
                bit = 1 if weight > 0 else 0
            
            # Construct the marking vector and accumulate the objective value.
            current_marking.append(bit)
            current_val += bit * weight

        # Update the global maximum if the current marking is better.
        if current_val > max_val:
            max_val = current_val
            best_marking = current_marking

    return best_marking, max_val