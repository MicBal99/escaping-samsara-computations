from __future__ import annotations

from typing import Sequence

import numpy as np

from .d4 import canonical


def neighbours(n: int, idx: int) -> list[int]:
    i, j = divmod(idx, n)
    out = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            out.append(((i + di) % n) * n + ((j + dj) % n))
    return out


def legal_at(state: int, n: int, idx: int, B: set[int], S: set[int]) -> bool:
    bit = (state >> idx) & 1
    k = sum((state >> q) & 1 for q in neighbours(n, idx))
    return (k in B) if bit == 0 else (k not in S)


def window3_pattern(state: int, n: int, ci: int, cj: int) -> int:
    p = 0
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            idx = ((ci + di) % n) * n + ((cj + dj) % n)
            p = (p << 1) | ((state >> idx) & 1)
    return p


def global_potential(state: int, n: int, weights_by_pattern: Sequence[int]) -> int:
    total = 0
    for i in range(n):
        for j in range(n):
            total += int(weights_by_pattern[window3_pattern(state, n, i, j)])
    return total


def exhaustive_small_torus_check(weights_by_pattern: Sequence[int], B: set[int], S: set[int], n: int) -> tuple[int, tuple[int, int]]:
    """Return maximum exact integer ΔPhi over all legal single-cell updates on n x n torus."""
    total_states = 1 << (n * n)
    phi = [0] * total_states
    for state in range(total_states):
        phi[state] = global_potential(state, n, weights_by_pattern)
    max_delta = -10**30
    witness = (-1, -1)
    for state in range(total_states):
        for idx in range(n * n):
            if legal_at(state, n, idx, B, S):
                nxt = state ^ (1 << idx)
                d = phi[nxt] - phi[state]
                if d > max_delta:
                    max_delta = d
                    witness = (state, idx)
    return max_delta, witness
