# Claim-to-code map

This file maps the computer-supported statements in the audited thesis to reproducibility commands.

| Thesis location / claim | Command | Expected result |
|---|---|---|
| Method I, `B4/S34` simple ansatz | `python scripts/verify_method1_1d.py` | max ΔΦ = -1 |
| Method I, `B12/S0124` simple ansatz | same | max ΔΦ = -1 |
| Method I, D4 reduction | `python scripts/verify_method1_2d.py` | 102 binary 3x3 D4 orbits |
| Method I, `B3/S1234567`, n>=5 | same | 3,801,088 contexts; max scaled ΔΦ = -559162 |
| Method I, `B3/S12345`, n>=5 | same | 6,160,384 contexts; max scaled ΔΦ = -559162 |
| Method I, both 2D rules, n=3 | same | max scaled ΔΦ = -939878 |
| Method I, both 2D rules, n=4 | same | max scaled ΔΦ = -818600 |
| Method II, `B12/S12` delta table | `python scripts/verify_method2.py` | -3,-1,+5,-1,-3 |
| Method II, `B12/S12` N=7 cycle | same | all 8 edges legal; exactly two d0 moves |
| Method II, `B4/S2` context census | same | 336 / 151 / 25 |
| Method II, `B4/S2` de Bruijn Cover | same | 0 residual legal edges on a cycle |
| Method II, `B4/S2` small rings | same | all 480 states pass CLF condition |
| Method III, six-state interval | `python scripts/verify_method3.py` | hull M\\{b1}; 128 budgets |
| Method III, trap union | same | hull M\\{b2}; 64 budgets; B01/S234 |

Discovery/re-solving scripts:

- `python scripts/solve_method1_1d.py`
- `python scripts/solve_method1_2d.py`
- `python scripts/solve_method2_b4s2.py`

The verifier output, not a particular solver basis, is the authoritative reproducibility target.
