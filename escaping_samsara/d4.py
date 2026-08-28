from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import numpy as np


def int_to_matrix3(pattern: int) -> list[list[int]]:
    s = f"{pattern:09b}"
    return [[int(s[3 * i + j]) for j in range(3)] for i in range(3)]


def matrix3_to_int(m: list[list[int]]) -> int:
    out = 0
    for i in range(3):
        for j in range(3):
            out = (out << 1) | int(m[i][j])
    return out


def rotate90(m: list[list[int]]) -> list[list[int]]:
    return [[m[2 - j][i] for j in range(3)] for i in range(3)]


def reflect_vertical(m: list[list[int]]) -> list[list[int]]:
    return [list(reversed(row)) for row in m]


def orbit(pattern: int) -> tuple[int, ...]:
    m = int_to_matrix3(pattern)
    vals = []
    cur = m
    for _ in range(4):
        vals.append(matrix3_to_int(cur))
        cur = rotate90(cur)
    cur = reflect_vertical(m)
    for _ in range(4):
        vals.append(matrix3_to_int(cur))
        cur = rotate90(cur)
    return tuple(sorted(set(vals)))


def canonical(pattern: int) -> int:
    return min(orbit(pattern))


def canonical_tables() -> tuple[np.ndarray, list[int], dict[int, int]]:
    canon = np.array([canonical(p) for p in range(512)], dtype=np.uint16)
    reps = sorted(set(int(x) for x in canon))
    orbit_id = {p: i for i, p in enumerate(reps)}
    return canon, reps, orbit_id


def load_integer_weights(path: str | Path) -> tuple[np.ndarray, list[int], dict[int, int]]:
    canon, reps, orbit_id = canonical_tables()
    by_rep: dict[int, int] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = int(row["canonical_3x3_pattern_row_major"], 2)
            by_rep[p] = int(row["integer_weight_scale_1e6"])
    if set(by_rep) != set(reps):
        missing = sorted(set(reps) - set(by_rep))
        extra = sorted(set(by_rep) - set(reps))
        raise ValueError(f"weight table does not match D4 orbits; missing={missing}, extra={extra}")
    weights_by_pattern = np.array([by_rep[int(c)] for c in canon], dtype=np.int64)
    weights_by_orbit = np.array([by_rep[p] for p in reps], dtype=np.int64)
    return weights_by_pattern, reps, orbit_id


OUTER_POSITIONS = [(i, j) for i in range(5) for j in range(5) if not (1 <= i <= 3 and 1 <= j <= 3)]
AFFECTED_CENTERS = [(i, j) for i in range(1, 4) for j in range(1, 4)]


def _central_bit(pattern: int, i: int, j: int) -> int:
    return (pattern >> (8 - (3 * i + j))) & 1


def central_contributions() -> np.ndarray:
    out = np.zeros((512, 9), dtype=np.uint16)
    for p in range(512):
        for wi, (ci, cj) in enumerate(AFFECTED_CENTERS):
            value = 0
            for li, di in enumerate((-1, 0, 1)):
                for lj, dj in enumerate((-1, 0, 1)):
                    gi, gj = ci + di, cj + dj
                    if 1 <= gi <= 3 and 1 <= gj <= 3:
                        bit = _central_bit(p, gi - 1, gj - 1)
                        value |= bit << (8 - (3 * li + lj))
            out[p, wi] = value
    return out


def outer_contributions() -> np.ndarray:
    masks = np.arange(1 << 16, dtype=np.uint32)
    out = np.zeros((9, 1 << 16), dtype=np.uint16)
    outer_index = {pos: k for k, pos in enumerate(OUTER_POSITIONS)}
    for wi, (ci, cj) in enumerate(AFFECTED_CENTERS):
        arr = np.zeros(1 << 16, dtype=np.uint16)
        for li, di in enumerate((-1, 0, 1)):
            for lj, dj in enumerate((-1, 0, 1)):
                pos = (ci + di, cj + dj)
                if pos in outer_index:
                    k = outer_index[pos]
                    arr |= (((masks >> k) & 1).astype(np.uint16) << (8 - (3 * li + lj)))
        out[wi] = arr
    return out


def legal_central_patterns(B: set[int], S: set[int]) -> list[int]:
    out: list[int] = []
    for p in range(512):
        bits = [int(c) for c in f"{p:09b}"]
        center = bits[4]
        neighbours = sum(bits) - center
        legal = (neighbours in B) if center == 0 else (neighbours not in S)
        if legal:
            out.append(p)
    return out


def exhaustive_local_check(weights_by_pattern: np.ndarray, B: set[int], S: set[int]) -> tuple[int, int, tuple[int, int]]:
    central = central_contributions()
    outer = outer_contributions()
    legal = legal_central_patterns(B, S)
    max_delta = -10**30
    witness = (-1, -1)
    center_toggle = 1 << 4
    for p in legal:
        q = p ^ center_toggle
        total_before = np.zeros(1 << 16, dtype=np.int64)
        total_after = np.zeros(1 << 16, dtype=np.int64)
        for wi in range(9):
            pat_before = outer[wi] | central[p, wi]
            pat_after = outer[wi] | central[q, wi]
            total_before += weights_by_pattern[pat_before]
            total_after += weights_by_pattern[pat_after]
        delta = total_after - total_before
        idx = int(np.argmax(delta))
        val = int(delta[idx])
        if val > max_delta:
            max_delta = val
            witness = (p, idx)
    return len(legal) * (1 << 16), max_delta, witness


def context_relator_102(central_pattern: int, outer_mask: int, orbit_id: dict[int, int]) -> np.ndarray:
    canon, reps, _ = canonical_tables()
    grid = [[0] * 5 for _ in range(5)]
    s = f"{central_pattern:09b}"
    for i in range(3):
        for j in range(3):
            grid[i + 1][j + 1] = int(s[3 * i + j])
    for k, (i, j) in enumerate(OUTER_POSITIONS):
        grid[i][j] = (outer_mask >> k) & 1

    def pat_at(ci: int, cj: int) -> int:
        value = 0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                value = (value << 1) | grid[ci + di][cj + dj]
        return value

    before = [pat_at(i, j) for i, j in AFFECTED_CENTERS]
    grid[2][2] ^= 1
    after = [pat_at(i, j) for i, j in AFFECTED_CENTERS]
    row = np.zeros(len(reps), dtype=np.int16)
    for p in after:
        row[orbit_id[int(canon[p])]] += 1
    for p in before:
        row[orbit_id[int(canon[p])]] -= 1
    return row
