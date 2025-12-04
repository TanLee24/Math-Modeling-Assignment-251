import collections

# --- Python 3.10+ compatibility fix for PyEDA ---
try:
    collections.Sequence = collections.abc.Sequence
except AttributeError:
    pass
# -------------------------------------------------

from pyeda.inter import *
import numpy as np
from typing import Tuple
from .task1_PetriNet import PetriNet

# Constant BDDs
ONE = expr2bdd(expr("1"))
ZERO = expr2bdd(expr("0"))

def bdd_reachable(pn: PetriNet) -> Tuple[BinaryDecisionDiagram, int]:
    """
    Compute the reachable markings of a 1-safe Petri net using BDD-based symbolic exploration.
    Automatically normalizes unsafe variable names (UUIDs) into safe PyEDA-compatible names.
    """

    num_places = len(pn.place_ids)

    # ---------------------------
    # 1. Create BDD variables
    # ---------------------------
    # If a place_id has a valid variable name (alphabetic start, alphanumeric/underscore),
    # use it directly (for test cases). Otherwise fallback to p0, p1, ...
    X = []
    X_prime = []

    for i, pid in enumerate(pn.place_ids):
        if pid and pid[0].isalpha() and all(c.isalnum() or c == "_" for c in pid):
            name = pid          # keep original name (e.g., p1, P2, ...)
        else:
            name = f"p{i+1}"      # invalid name (UUID) → replace by safe p{i}

        X.append(bddvar(name))              # current-state variable
        X_prime.append(bddvar(name + "_prime"))  # next-state variable

    # rename X' → X after transition firing
    rename_map = {X_prime[i]: X[i] for i in range(num_places)}

    # ---------------------------
    # 2. Encode initial marking M0
    # ---------------------------
    S = ONE
    for i in range(num_places):
        S &= X[i] if pn.M0[i] == 1 else ~X[i]

    # ---------------------------
    # 3. Build transition relation R
    # ---------------------------
    R = ZERO
    num_trans = len(pn.I)

    for t in range(num_trans):
        input_vec = pn.I[t]
        output_vec = pn.O[t]

        # Enabling condition (transition can fire)
        enabling = ONE
        for i in range(num_places):
            if input_vec[i] == 1:
                enabling &= X[i]          # input place must contain a token
            if output_vec[i] == 1 and input_vec[i] == 0:
                enabling &= ~X[i]         # enforce 1-safety (place must be empty)

        # Post-transition marking (X → X')
        change = ONE
        for i in range(num_places):
            is_in = input_vec[i] == 1
            is_out = output_vec[i] == 1

            if is_in and not is_out:
                change &= ~X_prime[i]         # token consumed
            elif is_out:
                change &= X_prime[i]          # token produced
            else:
                change &= ~(X[i] ^ X_prime[i])  # unchanged (XNOR)

        R |= (enabling & change)

    # ---------------------------
    # 4. Fixpoint: symbolic reachability
    # ---------------------------
    while True:
        # Compute S × R (image)
        step = S & R
        img = step.smoothing(X)            # eliminate current-state vars
        nxt = img.compose(rename_map)      # rename X' → X

        new_states = nxt & ~S              # newly discovered markings
        if new_states.is_zero():
            break                           # fixed point reached

        S |= nxt

    
    # Replace old satisfy_count() due to bug with don't-cares
    count = 0
    for i in range(2 ** num_places):
        # Generate marking from binary representation
        marking = tuple((i >> j) & 1 for j in range(num_places))
        # Check if this marking is in the reachable set
        constraint = ONE
        for j in range(num_places):
            constraint &= X[j] if marking[j] == 1 else ~X[j]
        if not (S & constraint).is_zero():
            count += 1
    
    # Return reachable set BDD and number of satisfying assignments
    return S, count
