#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from escaping_samsara.one_d import Rule1D, all_contexts, legal_center_context5, simple_ansatz_delta_vector

CASES = [
    ("B4/S34", Rule1D.from_sets({4}, {3, 4})),
    ("B12/S0124", Rule1D.from_sets({1, 2}, {0, 1, 2, 4})),
]


def main() -> None:
    for name, rule in CASES:
        rows = [simple_ansatz_delta_vector(ctx) for ctx in all_contexts(5) if legal_center_context5(ctx, rule)]
        A = np.asarray(rows, dtype=float)
        b = -np.ones(len(rows))
        result = linprog(c=np.zeros(3), A_ub=A, b_ub=b, bounds=[(None, None)] * 3, method="highs")
        if not result.success:
            raise RuntimeError(f"{name}: solver failed: {result.message}")
        margin = max(A @ result.x)
        print(f"{name}: feasible coefficients {result.x.tolist()}, max Δ={margin:.12g}")


if __name__ == "__main__":
    main()
