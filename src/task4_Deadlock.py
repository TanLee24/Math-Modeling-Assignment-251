import pulp
from typing import List, Optional
from pyeda.inter import *
from .task1_PetriNet import PetriNet

def deadlock_reachable_marking(
    pn: PetriNet,
    bdd: BinaryDecisionDiagram,
) -> Optional[List[int]]:

    model, x, y = ILP_variable_setup(pn)
    ILP_add_dead_constraints(model, x, y, pn)
    add_objective(model, x)

    while True:
        candidate = candidate_from_ILP(model, x)
        if candidate is None:
            return None     # No more ILP solutions

        if is_reachable(candidate, pn, bdd):
            return candidate

        add_exclusion_constraint(model, x, candidate, pn)


# ILP Setup
def ILP_variable_setup(pn: PetriNet):
    model = pulp.LpProblem("DeadlockSearch", pulp.LpMinimize)

    # marking variables
    x = {p: pulp.LpVariable(f"x_{p}", cat="Binary") for p in pn.place_ids}

    # OR-selector variables (one per transition)
    y = {t: pulp.LpVariable(f"y_{t}", cat="Binary") for t in pn.trans_ids}

    return model, x, y


def ILP_add_dead_constraints(model, x, y, pn: PetriNet):
    # Add constraints: every transition must be disabled
    T, P = pn.I.shape

    for t in range(T):
        pre = [pn.place_ids[i] for i in range(P) if pn.I[t][i] == 1]
        out_only = [pn.place_ids[i] for i in range(P) if pn.O[t][i] == 1 and pn.I[t][i] == 0]
        y_t = y[pn.trans_ids[t]]

        # Transition with no pre-places
        if not pre:
            if out_only:
                model += y_t == 1
                model += pulp.lpSum(x[p] for p in out_only) >= 1
            else:
                # impossible to disable -> no deadlock possible
                model += 0 <= -1
            continue

        # OR encoding:
        # A: some pre-place is 0
        # B: some output-only place is 1
        bigM = len(pre)

        model += pulp.lpSum(x[p] for p in pre) <= len(pre) - 1 + bigM * y_t

        if out_only:
            model += pulp.lpSum(x[p] for p in out_only) >= y_t
        else:
            model += y_t == 0


def add_objective(model, x):
    model += pulp.lpSum(x.values())


def add_exclusion_constraint(model, x, candidate, pn):
    # Exclude previous candidate so ILP finds a new one
    diff = []
    for i, p in enumerate(pn.place_ids):
        diff.append(1 - x[p] if candidate[i] == 1 else x[p])
    model += pulp.lpSum(diff) >= 1


def candidate_from_ILP(model, x):
    # Solves ILP, return a marking if exists, otherwise return None
    model.solve(pulp.PULP_CBC_CMD(msg=False))

    status = pulp.LpStatus[model.status]
    if status in ("Infeasible", "Undefined"):
        return None
    return [int(pulp.value(x[p])) for p in x]


# BDD checking reachables
def is_reachable(candidate, pn: PetriNet, bdd: BinaryDecisionDiagram):
    assign = {}
    for var in bdd.support:
        name = var.name      # ex: "p3"
        idx = int(name[1:])  # take the mum 3
        assign[var] = candidate[idx]

    return bdd.restrict(assign).is_one()
