from collections import deque
import numpy as np
from .task1_PetriNet import PetriNet
from typing import Set, Tuple

def dfs_reachable(pn: PetriNet) -> Set[Tuple[int, ...]]:
    """
    Computes the set of reachable markings using Depth-First Search (DFS).
    
    This function explores the state space of a 1-safe Petri net starting from
    the initial marking M0. It uses a stack data structure to traverse
    markings depth-wise.
    
    Args:
        pn (PetriNet): The Petri net model containing structure (I, O matrices)
                       and initial state (M0).
                       
    Returns:
        Set[Tuple[int, ...]]: A set of unique reachable markings, where each
                              marking is represented as a tuple of integers.
    """
    
    # Initialize the set of visited markings to avoid processing duplicates
    # Store markings as tuples because numpy arrays are not hashable
    visited = set()
    m0_tuple = tuple(pn.M0)
    visited.add(m0_tuple)
    
    # Initialize the stack with the initial marking (LIFO structure for DFS)
    # Using a python list as a stack (append/pop)
    stack = [pn.M0]
    
    # Cache the number of transitions for efficiency in the loop
    num_transitions = len(pn.I)
    
    while stack:
        # Pop the last added marking (Depth-First strategy)
        current_m = stack.pop()
        
        # Iterate over all transitions to find enabled ones
        for t in range(num_transitions):
            # Retrieve input and output incidence vectors for transition t
            input_vector = pn.I[t]
            output_vector = pn.O[t]
            
            # Check the enabling condition: M >= Pre(t)
            # A transition is enabled if all its input places have sufficient tokens
            if np.all(current_m >= input_vector):
                # Fire the transition: M' = M - Pre(t) + Post(t)
                next_m = current_m - input_vector + output_vector
                
                # --- Constraint Check: 1-Safe Property ---
                # A 1-safe Petri net must not have more than 1 token in any place.
                # If firing transition t violates this property, discard the new marking.
                if np.any(next_m > 1):
                    continue
                # -----------------------------------------

                # Convert the new marking to a tuple for hashing
                next_m_tuple = tuple(next_m)
                
                # If this state has not been visited yet, add it to the set and stack
                if next_m_tuple not in visited:
                    visited.add(next_m_tuple)
                    stack.append(next_m)
                    
    return visited