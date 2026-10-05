"""Orakel-Test: Branch & Bound gegen scipy.optimize.milp (Zuordnungsmodell), Schranken gegen die exakte Vervollständigung per DP,
Knotenzahlen gegen eine unabhängige, rekursionsfreie Tiefensuche, und das Aufrufbudget der Bruteforce-Gegenprobe der App."""

import random
import time
from functools import lru_cache

import numpy as np
import pytest

from csbb_bounds import strong_bound, weak_bound
from csbb_bruteforce import solve_bruteforce
from csbb_constants import MAX_BRUTEFORCE_CALLS
from csbb_scenario import CuttingStockInstance, expand_pieces, generate_instance
from csbb_solver import solve

optimize = pytest.importorskip("scipy.optimize")


def _milp_optimum(pieces, width):
    n = len(pieces)
    nv = n * n + n                                   # x[i, k] Stück i in Bin k, y[k] Bin k benutzt
    cost = np.zeros(nv)
    cost[n * n:] = 1
    rows, lo, hi = [], [], []
    for i in range(n):
        r = np.zeros(nv)
        r[i * n:(i + 1) * n] = 1
        rows.append(r)
        lo.append(1)
        hi.append(1)
    for k in range(n):
        r = np.zeros(nv)
        for i in range(n):
            r[i * n + k] = pieces[i]
        r[n * n + k] = -width
        rows.append(r)
        lo.append(-np.inf)
        hi.append(0)
    res = optimize.milp(cost, constraints=optimize.LinearConstraint(np.array(rows), lo, hi), integrality=np.ones(nv), bounds=optimize.Bounds(0, 1))
    return int(round(res.fun))


def _independent_dfs_nodes(pieces, width, bound_fn, instance, merge):
    """Knotenzahl und Optimum einer eigenen Tiefensuche mit explizitem Stapel (gleiche Regeln: Optionen in Bin-Reihenfolge, neues Bin zuletzt)."""
    n = len(pieces)

    def options(depth, bins):
        out, seen = [], set()
        for i, cap in enumerate(bins):
            if merge:
                if cap in seen:
                    continue
                seen.add(cap)
            if cap >= pieces[depth]:
                nb = list(bins)
                nb[i] -= pieces[depth]
                out.append(nb)
        out.append(list(bins) + [width - pieces[depth]])
        return out

    nodes, best = 1, None
    stack = [(0, options(0, []), 0)]
    while stack:
        depth, opts, idx = stack.pop()
        if idx >= len(opts):
            continue
        stack.append((depth, opts, idx + 1))
        nb = opts[idx]
        nodes += 1
        if depth + 1 == n:
            best = len(nb) if best is None else min(best, len(nb))
            continue
        if best is not None and bound_fn(instance, pieces, depth + 1, nb) >= best:
            continue
        stack.append((depth + 1, options(depth + 1, nb), 0))
    return nodes, best


def test_branch_and_bound_equals_milp_and_an_independent_search():
    rng = random.Random(77)
    checked = 0
    for t in range(80):
        if t < 50:
            inst = generate_instance(rng.randint(2, 5), rng.choice((50, 100, 137, 200)), rng.randint(1, 3), rng.randint(0, 10**6))
        else:                                        # Randfälle: Breite = Rollenbreite, Breite 1, sehr kleine Rollen
            width = rng.choice((1, 2, 5, 10, 17))
            nt = rng.randint(1, 3)
            inst = CuttingStockInstance(width, tuple(rng.randint(1, width) for _ in range(nt)), tuple(rng.randint(1, 3) for _ in range(nt)))
        pieces = expand_pieces(inst)
        if len(pieces) > 11:
            continue
        ref = _milp_optimum(list(pieces), inst.roll_width)
        for bound_fn in (weak_bound, strong_bound):
            for merge in (False, True):
                res = solve(inst, bound_fn, skip_equivalent_bins=merge)
                assert not res.truncated and res.best_value == ref
                assert sum(inst.roll_width - c for c in res.best_bins) == sum(pieces) and len(res.best_bins) == ref
                assert (len(res.nodes), res.best_value) == _independent_dfs_nodes(pieces, inst.roll_width, bound_fn, inst, merge)
        checked += 1
    assert checked >= 60


def _min_total_bins(pieces, width, depth, bins):
    @lru_cache(None)
    def f(idx, caps):
        if idx == len(pieces):
            return len(caps)
        p = pieces[idx]
        best = f(idx + 1, tuple(sorted(caps + (width - p,))))
        for i, c in enumerate(caps):
            if c >= p:
                nc = list(caps)
                nc[i] -= p
                best = min(best, f(idx + 1, tuple(sorted(nc))))
        return best
    return f(depth, tuple(sorted(bins)))


def test_bounds_never_exceed_the_exact_completion_on_random_partial_packings():
    rng = random.Random(5)
    for _ in range(150):
        width = rng.choice((10, 20, 50, 100))
        pieces = tuple(sorted((rng.randint(max(1, width // 6), (3 * width) // 5) for _ in range(rng.randint(1, 8))), reverse=True))
        inst = CuttingStockInstance(width, pieces, tuple(1 for _ in pieces))
        depth = rng.randint(0, len(pieces))
        bins = []
        for p in pieces[:depth]:
            fits = [i for i, c in enumerate(bins) if c >= p]
            if fits and rng.random() < 0.7:
                bins[rng.choice(fits)] -= p
            else:
                bins.append(width - p)
        true_min = _min_total_bins(pieces, width, depth, tuple(bins))
        for bound_fn in (weak_bound, strong_bound):
            assert bound_fn(inst, pieces, depth, list(bins)) <= true_min


def test_bruteforce_budget_stops_the_slow_reference_quickly():
    """Regression: die App rief die unbeschränkte Bruteforce-Enumeration immer auf; auf manchen Instanzen im Reglerbereich (6 Typen, Bedarf 4)
    dauerte sie Minuten (bis 373 s gemessen) und die Seite hing."""
    inst = generate_instance(6, 100, 4, 60)
    start = time.time()
    assert solve_bruteforce(inst, max_calls=MAX_BRUTEFORCE_CALLS) is None
    assert time.time() - start < 10
    small = generate_instance(3, 100, 2, 1)
    assert solve_bruteforce(small, max_calls=MAX_BRUTEFORCE_CALLS) == solve_bruteforce(small)
