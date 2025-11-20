import time


class BddManager:
    def __init__(self, var_list):
        self.vars = var_list
        self.unique = {}
        self.apply_cache = {}
        self.exists_cache = {}
        self.neg_cache = {}
        self.T = object()
        self.F = object()

    def var(self, name):
        return self._make(name, self.F, self.T)

    def _make(self, var, low, high):
        if low is high:
            return low
        key = (var, id(low), id(high))
        if key not in self.unique:
            self.unique[key] = (var, low, high)
        return self.unique[key]

    def apply(self, op, a, b):
        key = (op, id(a), id(b))
        if key in self.apply_cache:
            return self.apply_cache[key]

        # Terminal
        if a in (self.T, self.F) or b in (self.T, self.F):
            if op == "and":
                res = self.F if a is self.F or b is self.F else (b if a is self.T else (a if b is self.T else self.F))
            else:  # OR
                res = self.T if a is self.T or b is self.T else (b if a is self.F else (a if b is self.F else self.T))
            self.apply_cache[key] = res
            return res

        # Recursive merge
        va, la, ha = a
        vb, lb, hb = b
        ia, ib = self.vars.index(va), self.vars.index(vb)

        if ia == ib:
            low = self.apply(op, la, lb)
            high = self.apply(op, ha, hb)
        elif ia < ib:
            low = self.apply(op, la, b)
            high = self.apply(op, ha, b)
        else:
            low = self.apply(op, a, lb)
            high = self.apply(op, a, hb)

        res = self._make(self.vars[min(ia, ib)], low, high)
        self.apply_cache[key] = res
        return res

    def negate(self, n):
        if n is self.T: return self.F
        if n is self.F: return self.T
        if id(n) in self.neg_cache: return self.neg_cache[id(n)]
        var, l, h = n
        res = self._make(var, self.negate(l), self.negate(h))
        self.neg_cache[id(n)] = res
        return res

    def exists(self, node, qvars):
        key = (id(node), frozenset(qvars))
        if key in self.exists_cache:
            return self.exists_cache[key]

        if node in (self.T, self.F):
            return node

        var, low, high = node
        if var in qvars:
            res = self.apply("or", self.exists(low, qvars), self.exists(high, qvars))
        else:
            res = self._make(var, self.exists(low, qvars), self.exists(high, qvars))

        self.exists_cache[key] = res
        return res

    def rename(self, n, mapping):
        if n in (self.T, self.F): return n
        v, l, h = n
        nv = mapping.get(v, v)
        return self._make(nv, self.rename(l, mapping), self.rename(h, mapping))


# ============================
# SYMBOLIC REACHABILITY
# ============================

def symbolic_reachability(net):
    start_time = time.time()
    places = sorted(net.places)
    n = len(places)

    # --- SỬA LỖI QUAN TRỌNG: THỨ TỰ BIẾN (INTERLEAVING) ---
    # Thay vì để hết x rồi đến hết y, ta xếp xen kẽ: x0, y0, x1, y1...
    # Điều này giúp giảm kích thước BDD đi hàng nghìn lần.
    var_list = []
    for i in range(n):
        var_list.append(f'x{i}')
        var_list.append(f'y{i}')
    
    bdd = BddManager(var_list)
    x = {p: bdd.var(f'x{i}') for i, p in enumerate(places)}
    y = {p: bdd.var(f'y{i}') for i, p in enumerate(places)}

    # --- BƯỚC 1: XÂY DỰNG TRANSITION RELATION ---
    R = bdd.F
    
    # Cache lại logic "giữ nguyên" (x == y) cho từng place để đỡ tính lại
    # identity_pairs[p] lưu BDD của (x[p] == y[p])
    identity_pairs = {}
    for p in places:
        match_1 = bdd.apply('and', x[p], y[p])
        match_0 = bdd.apply('and', bdd.negate(x[p]), bdd.negate(y[p]))
        identity_pairs[p] = bdd.apply('or', match_1, match_0)

    for t in net.transitions:
        pre = net.get_preset(t)
        post = net.get_postset(t)

        # 1. Enabled Condition: Pre places phải là 1
        enabled = bdd.T
        for p in pre:
            enabled = bdd.apply('and', enabled, x[p])

        # 2. Next State & Frame Axiom
        # Thay vì tính lại từ đầu, ta dùng identity_pairs đã cache
        change = bdd.T
        for p in places:
            if p in post:
                change = bdd.apply('and', change, y[p])
            elif p in pre:
                change = bdd.apply('and', change, bdd.negate(y[p]))
            else:
                # Frame Axiom: Place không liên quan thì giữ nguyên
                change = bdd.apply('and', change, identity_pairs[p])

        # R_t = Enabled AND Change
        Rt = bdd.apply('and', enabled, change)
        R = bdd.apply('or', R, Rt)

    # --- BƯỚC 2 & 3 & 4: GIỮ NGUYÊN NHƯ CŨ ---
    # (Phần Initial Marking, count_sat và Fixed-point loop giữ nguyên không đổi)
    
    # --- Initial Marking ---
    S0 = bdd.T
    for p in places:
        if p in net.initial_marking:
            S0 = bdd.apply('and', S0, x[p])
        else:
            S0 = bdd.apply('and', S0, bdd.negate(x[p]))

    # --- Helper count ---
    def count_sat(node, var_set):
        cache = {}
        def count_rec(n, remaining_vars):
            if n is bdd.T: return 2 ** len(remaining_vars)
            if n is bdd.F: return 0
            key = (id(n), frozenset(remaining_vars))
            if key in cache: return cache[key]
            var, low, high = n
            if var not in var_set:
                res = count_rec(low, remaining_vars) + count_rec(high, remaining_vars)
            else:
                new_rem = remaining_vars - {var}
                res = count_rec(low, new_rem) + count_rec(high, new_rem)
            cache[key] = res
            return res
        return count_rec(node, var_set)

    reachable = S0
    x_vars = {f'x{i}' for i in range(n)}
    
    # --- Fixed Point Loop ---
    while True:
        old_count = count_sat(reachable, x_vars)
        img = bdd.apply('and', reachable, R)
        img = bdd.exists(img, x_vars)
        
        # Rename map cần tạo lại do thứ tự biến thay đổi (logic vẫn vậy)
        rename_map = {f'y{i}': f'x{i}' for i in range(n)}
        img = bdd.rename(img, rename_map)
        
        reachable = bdd.apply('or', reachable, img)
        new_count = count_sat(reachable, x_vars)
        
        if new_count == old_count:
            break

    elapsed = time.time() - start_time
    node_count = len(bdd.unique)
    return reachable, new_count, elapsed, node_count