from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Sequence

MOVE_TYPES = tuple([f"b{i}" for i in range(5)] + [f"d{i}" for i in range(5)])


@dataclass(frozen=True)
class Rule1D:
    B: frozenset[int]
    S: frozenset[int]

    @classmethod
    def from_sets(cls, B: Iterable[int], S: Iterable[int]) -> "Rule1D":
        return cls(frozenset(B), frozenset(S))

    @property
    def budget(self) -> frozenset[str]:
        return frozenset([*(f"b{i}" for i in self.B), *(f"d{i}" for i in range(5) if i not in self.S)])


def bits_of_state(state: int, n: int) -> list[int]:
    return [(state >> i) & 1 for i in range(n)]


def state_from_bits(bits: Sequence[int]) -> int:
    out = 0
    for i, bit in enumerate(bits):
        out |= (int(bit) & 1) << i
    return out


def live_neighbour_count_radius2(state: int, n: int, v: int) -> int:
    return sum((state >> ((v + off) % n)) & 1 for off in (-2, -1, 1, 2))


def move_type_at(state: int, n: int, v: int) -> str:
    bit = (state >> v) & 1
    s = live_neighbour_count_radius2(state, n, v)
    return ("b" if bit == 0 else "d") + str(s)


def legal_at(state: int, n: int, v: int, rule: Rule1D) -> bool:
    bit = (state >> v) & 1
    s = live_neighbour_count_radius2(state, n, v)
    if bit == 0:
        return s in rule.B
    return s not in rule.S


def legal_moves(state: int, n: int, rule: Rule1D) -> list[int]:
    return [v for v in range(n) if legal_at(state, n, v, rule)]


def flip(state: int, v: int) -> int:
    return state ^ (1 << v)


def cyclic_word(state: int, n: int, center: int, radius: int) -> tuple[int, ...]:
    return tuple((state >> ((center + off) % n)) & 1 for off in range(-radius, radius + 1))


def word_to_int(word: Sequence[int]) -> int:
    out = 0
    for bit in word:
        out = (out << 1) | int(bit)
    return out


def local_window_int(state: int, n: int, center: int, radius: int) -> int:
    return word_to_int(cyclic_word(state, n, center, radius))


def additive_window_potential(state: int, n: int, radius: int, weights: Sequence[int]) -> int:
    expected = 1 << (2 * radius + 1)
    if len(weights) != expected:
        raise ValueError(f"expected {expected} weights, got {len(weights)}")
    return sum(weights[local_window_int(state, n, v, radius)] for v in range(n))


def local_delta_from_context(context: int, context_radius: int, potential_radius: int, weights: Sequence[int]) -> int:
    """Potential change when the central bit of a local context is flipped.

    The context is a binary word of length 2*context_radius+1 encoded as an int,
    with the leftmost bit most significant. This routine is intended for the
    no-aliasing local checks used in the thesis.
    """
    length = 2 * context_radius + 1
    bits = [(context >> (length - 1 - i)) & 1 for i in range(length)]
    center = context_radius
    affected_centers = range(center - potential_radius, center + potential_radius + 1)

    def total(current: list[int]) -> int:
        s = 0
        for c in affected_centers:
            lo = c - potential_radius
            hi = c + potential_radius + 1
            s += weights[word_to_int(current[lo:hi])]
        return s

    before = total(bits)
    bits[center] ^= 1
    after = total(bits)
    return after - before


def simple_ansatz_delta_vector(context5: Sequence[int]) -> tuple[int, int, int]:
    """Return (ΔH, ΔP1, ΔP2) for flipping the centre of a 5-bit context."""
    if len(context5) != 5:
        raise ValueError("context must have length 5")
    b = list(map(int, context5))
    before_center = b[2]
    after_center = 1 - before_center
    dH = after_center - before_center

    # Only pairs touching the centre can change.
    dP1 = (after_center * b[1] + after_center * b[3]) - (before_center * b[1] + before_center * b[3])
    dP2 = (after_center * b[0] + after_center * b[4]) - (before_center * b[0] + before_center * b[4])
    return dH, dP1, dP2


def legal_center_context5(context5: Sequence[int], rule: Rule1D) -> bool:
    b = list(map(int, context5))
    center = b[2]
    s = b[0] + b[1] + b[3] + b[4]
    return (s in rule.B) if center == 0 else (s not in rule.S)


def all_contexts(length: int):
    for bits in product((0, 1), repeat=length):
        yield bits
