from .task1_PetriNet import PetriNet
from .task2_BFS import bfs_reachable
from .task3_BDD import bdd_reachable
from .task4_Deadlock import deadlock_detecting
from .task5_Optimization import max_reachable_marking
from pyeda.inter import *
import numpy as np
import time
import tracemalloc   # <-- added

# Function to measure time + memory
def measure(func, *args):
    tracemalloc.start()
    start_t = time.perf_counter()

    result = func(*args)

    end_t = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"   Time: {end_t - start_t:.6f} sec")
    print(f"   Memory used: {current / 1024:.2f} KB")

    return result, end_t - start_t

def main():
    # ------------------------------------------------------
    # 1. Load Petri Net
    # ------------------------------------------------------
    filename = "tests/test1.pnml" # Change model file here!!!
    print("Loading PNML:", filename)

    start = time.perf_counter()
    pn = PetriNet.from_pnml(filename)
    load_time = time.perf_counter() - start

    print("\n--- Petri Net Loaded ---")
    print(pn)

    # ------------------------------------------------------
    # 2. BFS reachable
    # ------------------------------------------------------
    print("\n--- BFS Reachable Markings ---")
    (bfs_set), bfs_time = measure(bfs_reachable, pn)

    # for m in bfs_set:
    #     print(np.array(m))
    print("Total BFS reachable =", len(bfs_set))

    # ------------------------------------------------------
    # 3. BDD reachable
    # ------------------------------------------------------
    print("\n--- BDD Reachable Markings ---")
    (bdd_result), bdd_time = measure(bdd_reachable, pn)
    bdd, count = bdd_result

    print("--- Satisfying assignments ---")
    for sat in bdd.satisfy_all():
        line = ", ".join(f"{var.names[0]}={val}" for var, val in sat.items())
        print(line)
    print("BDD reachable markings =", count)

    # ------------------------------------------------------
    # 4. Deadlock detection
    # ------------------------------------------------------
    print("\n--- Deadlock Detecting ---")
    (dead), deadlock_time = measure(deadlock_detecting, pn, bdd)

    if dead is not None:
        print("Deadlock marking:", dead)
    else:
        print("No deadlock reachable.")

    # ------------------------------------------------------
    # 5. Optimization: maximize c·M
    # ------------------------------------------------------
    c = np.array([-1, -2, 4, -3, -3, 0, -5, -2, 4, 4])
    print("\n--- Optimize c·M ---")

    (opt_result), opt_time = measure(max_reachable_marking, pn.place_names, bdd, c)
    max_mark, max_val = opt_result

    print("c:", c)
    print("Max marking:", max_mark)
    print("Max value:", max_val)

if __name__ == "__main__":
    main()
