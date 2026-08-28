# Escaping Samsara — computational supplement

Reproducibility code for the thesis

> **Escaping Samsara: Fixability in Totally Asynchronous Cellular Automata**  
> Michał Bałwanowski, University of Wrocław, 2026.

This repository contains the solvers, exhaustive enumerators, graph checks, and independent verifiers for every claim in the thesis that relies materially on computer computation. The repository is self-contained: all exact certificate tables needed by the verifiers are stored under `data/`.

## Reproducibility principle

The repository deliberately separates **discovery** from **verification**.

- `solve_*.py` uses SciPy/HiGHS and floating-point linear programming to *find* candidate certificates.
- `verify_*.py` does **not** trust solver tolerances. The final thesis certificates are rechecked by finite exhaustive enumeration, using exact integer arithmetic for all potential changes.

Thus the mathematical claims do not depend on the LP solver returning the same floating-point solution on another machine.

The exact certificate tables in `data/` are the tables used in the audited thesis version.

## Quick start

Python 3.10+ is sufficient. The code was last tested with Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
python scripts/run_all.py
```

Expected final line:

```text
ALL REQUESTED CHECKS PASSED
```

To re-run the solver stages as well:

```bash
python scripts/run_all.py --solvers
```

## What is verified

### Method I — simple one-dimensional Lyapunov ansatz

`python scripts/verify_method1_1d.py` checks every legal radius-two local context for the two explicit potentials in the thesis:

| rule | coefficients `(a,b,c)` in `a H + b P1 + c P2` | verified worst ΔΦ |
|---|---:|---:|
| `B4/S34` | `(3,-1,-1)` | `-1` |
| `B12/S0124` | `(-5,2,2)` | `-1` |

`python scripts/solve_method1_1d.py` reconstructs these coefficients using HiGHS.

### Method I — two-dimensional `3x3` D4-symmetric certificate

The exact 102 orbit weights are stored in `data/d4_weights.csv`.

`python scripts/verify_method1_2d.py` independently checks:

1. binary `3x3` windows have exactly **102 D4 orbits**;
2. `B3/S1234567`: all **3,801,088** legal `5x5` contexts satisfy `10^6 ΔΦ <= -559162`;
3. `B3/S12345`: all **6,160,384** legal `5x5` contexts satisfy the same bound;
4. small tori are checked globally: `n=3` has worst `10^6 ΔΦ=-939878`, and `n=4` has worst `10^6 ΔΦ=-818600`.

`python scripts/solve_method1_2d.py` is a deterministic cutting-plane LP search. The final theorem does not depend on reproducing the same floating-point basis because the stored integer certificate is checked exhaustively afterwards.

### Method II — `B12/S12`

`python scripts/verify_method2.py` checks the exact local potential-change table

```text
b1 -> -3
b2 -> -1
d0 -> +5
d3 -> -1
d4 -> -3
```

and independently verifies every edge of the explicit `N=7` cycle.

### Method II — `B4/S2`

The same script checks:

- the two `N=6` configurations used in the radius-one obstruction;
- the exact `336 / 151 / 25` context census;
- the de Bruijn/SCC Cover test, with zero residual legal edges on a directed cycle;
- all **480** states on the exceptional rings `N=5,6,7,8`.

The exact 32-entry radius-two weight table is stored in `data/b4s2_radius2_weights.csv` and `escaping_samsara/certificates.py`.

### Method III — samsara / kernel–hull certificates

`python scripts/verify_method3.py` reconstructs the five-cell examples directly from the definitions and checks:

- `U(C0)=M\{b1}`;
- minimum kernel `{b0,d0}`;
- **128** move budgets;
- union hull `M\{b2}`;
- kernel `{b0,b1,d1}`;
- **64** move budgets;
- example rule `B01/S234`.

## Solvers versus theorem checkers

| script | role | floating point? | final checker? |
|---|---|---:|---:|
| `solve_method1_1d.py` | LP discovery | yes | no |
| `solve_method1_2d.py` | cutting-plane LP discovery | yes | no |
| `solve_method2_b4s2.py` | LP re-solving | yes | no |
| `verify_method1_1d.py` | exhaustive exact verifier | no | yes |
| `verify_method1_2d.py` | exhaustive exact verifier | no | yes |
| `verify_method2.py` | enumeration + SCC/de Bruijn verifier | no | yes |
| `verify_method3.py` | enumeration + kernel/hull verifier | no | yes |

## Tests and CI

Run locally:

```bash
python -m unittest discover -s tests -v
```

`.github/workflows/verify.yml` runs the exact verification on every push and pull request. `solvers.yml` re-runs the discovery solvers manually.

## Independence notes

- SCCs are computed by a local Tarjan implementation; `networkx` is not used.
- The D4 orbit map is reconstructed from the eight rotations/reflections.
- The `5x5` checks enumerate every legal context; there is no random sampling.
- The `N=3,4` two-dimensional checks recompute the global torus potential.
- The `N=5..8` `B4/S2` check enumerates every global state.
