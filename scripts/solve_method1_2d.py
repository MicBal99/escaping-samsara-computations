#!/usr/bin/env python3
"""Discover a D4-symmetric 3x3-window Lyapunov certificate by cutting planes.

The LP solver is only a discovery tool. The independent verifier
`scripts/verify_method1_2d.py` checks the stored integer certificate over every
legal 5x5 context in exact integer arithmetic.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from escaping_samsara.d4 import (
    canonical_tables,
    exhaustive_local_check,
    central_contributions,
    legal_central_patterns,
    outer_contributions,
)


def pattern_orbit_indices() -> tuple[np.ndarray, list[int], dict[int, int]]:
    canon, reps, oid = canonical_tables()
    idx = np.array([oid[int(c)] for c in canon], dtype=np.int16)
    return idx, reps, oid


def separation_all(weights_orbit: np.ndarray, B: set[int], S: set[int]):
    idx, _, _ = pattern_orbit_indices()
    wpat = weights_orbit[idx]
    central = central_contributions()
    outer = outer_contributions()
    out = []
    for p in legal_central_patterns(B, S):
        q = p ^ (1 << 4)
        before = np.zeros(1 << 16, dtype=float)
        after = np.zeros(1 << 16, dtype=float)
        for wi in range(9):
            before += wpat[outer[wi] | central[p, wi]]
            after += wpat[outer[wi] | central[q, wi]]
        delta = after - before
        om = int(np.argmax(delta))
        out.append((float(delta[om]), p, om))
    return out


def relator_fast(central_pattern: int, outer_mask: int, canon: np.ndarray, oid: dict[int, int]) -> np.ndarray:
    grid = [[0] * 5 for _ in range(5)]
    bits = f"{central_pattern:09b}"
    for i in range(3):
        for j in range(3):
            grid[i + 1][j + 1] = int(bits[3 * i + j])
    from escaping_samsara.d4 import OUTER_POSITIONS, AFFECTED_CENTERS
    for k, (i, j) in enumerate(OUTER_POSITIONS):
        grid[i][j] = (outer_mask >> k) & 1
    def pat_at(ci: int, cj: int) -> int:
        v = 0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                v = (v << 1) | grid[ci + di][cj + dj]
        return v
    before = [pat_at(i, j) for i, j in AFFECTED_CENTERS]
    grid[2][2] ^= 1
    after = [pat_at(i, j) for i, j in AFFECTED_CENTERS]
    row = np.zeros(102, dtype=np.int16)
    for q in after:
        row[oid[int(canon[q])]] += 1
    for q in before:
        row[oid[int(canon[q])]] -= 1
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-margin", type=float, default=0.05)
    parser.add_argument("--max-iterations", type=int, default=60)
    parser.add_argument("--rule", choices=["B3/S12345", "B3/S1234567"], default="B3/S12345")
    args = parser.parse_args()

    B = {3}
    S = {1, 2, 3, 4, 5} if args.rule == "B3/S12345" else {1, 2, 3, 4, 5, 6, 7}
    canon, reps, oid = canonical_tables()
    nvars = len(reps)

    contexts = {(p, 0) for p in legal_central_patterns(B, S)}
    contexts |= {(p, (1 << 16) - 1) for p in legal_central_patterns(B, S)}

    solution = None
    for iteration in range(1, args.max_iterations + 1):
        rows = np.vstack([relator_fast(p, om, canon, oid) for p, om in sorted(contexts)]).astype(float)
        rhs = -args.target_margin * np.ones(rows.shape[0])
        res = linprog(c=np.zeros(nvars), A_ub=rows, b_ub=rhs, bounds=[(-1.0, 1.0)] * nvars, method="highs")
        if not res.success:
            raise RuntimeError(f"LP infeasible at iteration {iteration}: {res.message}")
        solution = res.x
        sep = separation_all(solution, B, S)
        worst, p, om = max(sep)
        print(f"iteration {iteration:3d}: constraints={len(contexts):5d}, worst Δ={worst:.9f}")
        if worst <= -args.target_margin + 1e-9:
            print("Finite separation oracle found no violating 5x5 context.")
            break
        added = 0
        for val, pp, oo in sep:
            if val > -args.target_margin + 1e-9 and (pp, oo) not in contexts:
                contexts.add((pp, oo)); added += 1
        if added == 0:
            raise RuntimeError("separation found a violation but no new context was added")
    else:
        raise RuntimeError("cutting-plane loop did not converge")

    assert solution is not None
    rounded = np.rint(solution * 1_000_000).astype(np.int64)
    print(f"rounded candidate integer weights (scale 1e6): {rounded.tolist()}")
    sep_round = separation_all(rounded.astype(float) / 1_000_000.0, B, S)
    worst_rounded, p, om = max(sep_round)
    print(f"rounded candidate worst Δ={worst_rounded:.9f}")
    if worst_rounded < 0:
        idx, _, _ = pattern_orbit_indices()
        exact_pattern_weights = rounded[idx].astype(np.int64)
        count, exact_max, _ = exhaustive_local_check(exact_pattern_weights, B, S)
        assert exact_max < 0
        print(f"rounded candidate exact integer check: contexts={count:,}, max scaled Δ={exact_max} [OK]")
    else:
        print("Rounded candidate lost strictness; use the stored exact certificate for verification.")


if __name__ == "__main__":
    main()
