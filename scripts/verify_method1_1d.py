#!/usr/bin/env python3
from __future__ import annotations

from escaping_samsara.one_d import Rule1D, all_contexts, legal_center_context5, simple_ansatz_delta_vector

CASES = [
    ("B4/S34", Rule1D.from_sets({4}, {3, 4}), (3, -1, -1), -1),
    ("B12/S0124", Rule1D.from_sets({1, 2}, {0, 1, 2, 4}), (-5, 2, 2), -1),
]


def main() -> None:
    for name, rule, coeffs, expected_max in CASES:
        deltas = []
        rows = []
        for ctx in all_contexts(5):
            if legal_center_context5(ctx, rule):
                vec = simple_ansatz_delta_vector(ctx)
                delta = sum(c * d for c, d in zip(coeffs, vec))
                deltas.append(delta)
                rows.append((ctx, vec, delta))
        got = max(deltas)
        assert got == expected_max, (name, got, expected_max)
        print(f"{name}: legal local contexts={len(rows)}, max ΔPhi={got} [OK]")


if __name__ == "__main__":
    main()
