from collections import deque
import numpy as np
from .task1_PetriNet import PetriNet
from typing import Set, Tuple

def bfs_reachable(pn: PetriNet) -> Set[Tuple[int, ...]]:
    """
    Computes the set of reachable markings using Breadth-First Search (BFS).
    
    This function explores the state space of a 1-safe Petri net level by level
    starting from the initial marking M0. It uses a queue data structure to
    ensure markings are processed in the order they are discovered.
    
    Args:
        pn (PetriNet): The Petri net model containing structure (I, O matrices)
                       and initial state (M0).
                       
    Returns:
        Set[Tuple[int, ...]]: A set of unique reachable markings, where each
                              marking is represented as a tuple of integers.
    """
    
    # Initialize the set of visited markings to avoid infinite loops
    visited = set()
    m0_tuple = tuple(pn.M0)
    visited.add(m0_tuple)
    
    # Initialize the queue with the initial marking (FIFO structure for BFS)
    # deque is optimized for fast appends and pops from both ends
    queue = deque([pn.M0])
    
    # Cache the total number of transitions
    num_transitions = len(pn.I)
    
    while queue:
        # Dequeue the oldest marking (Breadth-First strategy)
        current_m = queue.popleft()
        
        # Explore all possible transitions from the current state
        for t in range(num_transitions):
            # Get the input (consumption) and output (production) vectors
            input_vector = pn.I[t]
            output_vector = pn.O[t]
            
            # Check enabling condition: Are there enough tokens in input places?
            if np.all(current_m >= input_vector):
                # Calculate the resulting marking after firing transition t
                # Equation: M_next = M_curr - I[t] + O[t]
                next_m = current_m - input_vector + output_vector
                
                # --- Constraint Check: 1-Safe Property ---
                # Ensure the net remains 1-safe (max 1 token per place).
                # If the new marking contains any place with > 1 token, it is invalid.
                if np.any(next_m > 1):
                    continue
                # -----------------------------------------

                # Hashable representation for set storage
                next_m_tuple = tuple(next_m)
                
                # Add new state to visited set and enqueue for further exploration
                if next_m_tuple not in visited:
                    visited.add(next_m_tuple)
                    queue.append(next_m)
                    
    return visited