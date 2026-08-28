#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from escaping_samsara.d4 import canonical_tables, exhaustive_local_check, load_integer_weights
from escaping_samsara.two_d import exhaustive_small_torus_check

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "data" / "d4_weights.csv"
CASES = [
    ("B3/S1234567", {3}, {1, 2, 3, 4, 5, 6, 7}, 3_801_088),
    ("B3/S12345", {3}, {1, 2, 3, 4, 5}, 6_160_384),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-small-tori", action="store_true", help="skip global n=3,4 enumeration")
    args = parser.parse_args()

    _, reps, _ = canonical_tables()
    assert len(reps) == 102
    weights, _, _ = load_integer_weights(WEIGHTS)
    print("D4 orbits of binary 3x3 windows: 102 [OK]")

    for name, B, S, expected_count in CASES:
        count, max_delta, witness = exhaustive_local_check(weights, B, S)
        assert count == expected_count, (name, count, expected_count)
        assert max_delta == -559_162, (name, max_delta)
        print(f"{name}: legal 5x5 contexts={count:,}, max 1e6*ΔPhi={max_delta} [OK]")
        if not args.skip_small_tori:
            for n, expected in [(3, -939_878), (4, -818_600)]:
                got, w = exhaustive_small_torus_check(weights, B, S, n)
                assert got == expected, (name, n, got, expected)
                print(f"  n={n}: global max 1e6*ΔPhi={got} [OK]")


if __name__ == "__main__":
    main()
