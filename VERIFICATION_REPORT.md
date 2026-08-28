# Final local verification report

Date: 2026-08-28

Reference environment:

- Python 3.13.5
- NumPy 2.3.5
- SciPy 1.17.0

The complete exact verifier suite (`python scripts/run_all.py`) passed.

Verified outputs:

- `B4/S34`: 12 legal local contexts, maximum `Delta Phi = -1`.
- `B12/S0124`: 14 legal local contexts, maximum `Delta Phi = -1`.
- D4 orbits of binary 3x3 windows: 102.
- `B3/S1234567`: 3,801,088 legal 5x5 contexts, maximum scaled change `-559162`.
- `B3/S12345`: 6,160,384 legal 5x5 contexts, maximum scaled change `-559162`.
- Both 2D rules on `n=3`: global maximum scaled change `-939878`.
- Both 2D rules on `n=4`: global maximum scaled change `-818600`.
- `B12/S12`: exact delta table `b1=-3, b2=-1, d0=+5, d3=-1, d4=-3`; the printed N=7 cycle is legal and contains exactly two `d0` moves.
- `B4/S2`: context census `336 / 151 / 25`; no residual legal edge is on a directed cycle; all 480 states on N=5..8 pass the CLF check.
- Method III six-state certificate: hull `M\{b1}`, minimum kernel `{b0,d0}`, 128 budgets.
- Method III union certificate: hull `M\{b2}`, safe kernel `{b0,b1,d1}`, 64 budgets, example rule `B01/S234`.
- The machine-readable D4 table contains all 102 orbit weights used by the exact verifier.
- The machine-readable B4/S2 table contains the 32-entry radius-two certificate used by the exact verifier.

Solver checks were also run successfully:

- `solve_method1_1d.py` reproduces `(3,-1,-1)` and `(-5,2,2)`.
- `solve_method2_b4s2.py` finds a feasible potential for the fixed certified controller; after scaling by 3, the whole fixed constraint system has exact integer maximum `-3`.
- `solve_method1_2d.py` converges deterministically in 31 cutting-plane iterations at target margin `0.05`; its rounded 1e6-scaled candidate independently passes all 6,160,384 `B3/S12345` contexts with exact integer maximum `-49995`.
