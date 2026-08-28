from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def strongly_connected_components(vertices: Iterable[int], adjacency: dict[int, list[int]]) -> list[list[int]]:
    """Tarjan SCC, implemented locally to keep verification independent of networkx."""
    index = 0
    stack: list[int] = []
    on_stack: set[int] = set()
    indices: dict[int, int] = {}
    low: dict[int, int] = {}
    out: list[list[int]] = []

    def visit(v: int) -> None:
        nonlocal index
        indices[v] = low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)
        for w in adjacency.get(v, []):
            if w not in indices:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], indices[w])
        if low[v] == indices[v]:
            comp: list[int] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)
                if w == v:
                    break
            out.append(comp)

    for v in vertices:
        if v not in indices:
            visit(v)
    return out


def edge_on_directed_cycle(u: int, v: int, component_id: dict[int, int]) -> bool:
    return component_id[u] == component_id[v]
