from .task1_PetriNet import PetriNet
from .task2_BFS import bfs_reachable
from .task2_DFS import dfs_reachable
from .task3_BDD import bdd_reachable
from .task4_Deadlock import deadlock_reachable_marking
from .task5_Optimization import max_reachable_marking
from pyeda.inter import *
import pulp
import numpy as np

def main():
    # ------------------------------------------------------
    # 1. Load Petri Net from PNML file
    # ------------------------------------------------------
    filename = "tests/test.pnml"
    print("Loading PNML:", filename)

    pn = PetriNet.from_pnml(filename)
    print("\n--- Petri Net Loaded ---")
    print(pn)

    # ------------------------------------------------------
    # 2. BFS reachable
    # ------------------------------------------------------
    print("\n--- BFS Reachable Markings ---")
    bfs_set = bfs_reachable(pn)
    for m in bfs_set:
        print(np.array(m))
    print("Total BFS reachable =", len(bfs_set))

    # ------------------------------------------------------
    # 3. DFS reachable
    # ------------------------------------------------------
    print("\n--- DFS Reachable Markings ---")
    dfs_set = dfs_reachable(pn)
    for m in dfs_set:
        print(np.array(m))
    print("Total DFS reachable =", len(dfs_set))

    # ------------------------------------------------------
    # 4. BDD reachable
    # ------------------------------------------------------
    print("\n--- BDD Reachable ---")
    bdd, count = bdd_reachable(pn)
    print("Satisfying all:", list(bdd.satisfy_all()))
    print("Minimized =", espresso_exprs(bdd2expr(bdd)))
    print("BDD reachable markings =", count)
    ## Source(bdd.to_dot()).render("bdd", format="png", cleanup=True)

    # ------------------------------------------------------
    # 5. Deadlock detection
    # ------------------------------------------------------
    print("\n--- Deadlock reachable marking ---")
    dead = deadlock_reachable_marking(pn, bdd)
    if dead is not None:
        print("Deadlock marking:", dead)
    else:
        print("No deadlock reachable.")

    # ------------------------------------------------------
    # 6. Optimization: maximize c·M
    # ------------------------------------------------------
    c = np.array([1, -2, 3, -1, 1, 2])
    print("\n--- Optimize c·M ---")
    max_mark, max_val = max_reachable_marking(
        pn.place_names, bdd, c
    )
    print("c:", c)
    print("Max marking:", max_mark)
    print("Max value:", max_val)


if __name__ == "__main__":
    main()
