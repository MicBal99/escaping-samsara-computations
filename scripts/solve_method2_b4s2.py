#!/usr/bin/env python3
"""Re-solve the radius-2 B4/S2 CLF after fixing the certified controller."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from escaping_samsara.one_d import Rule1D, flip, legal_moves, local_delta_from_context, local_window_int
from escaping_samsara.certificates import B4S2_RADIUS2_WEIGHTS as B4S2_WEIGHTS


def _bits9(ctx:int): return [(ctx>>(8-i))&1 for i in range(9)]
def b4s2_legal_context(ctx:int)->bool:
    b=_bits9(ctx); center=b[4]; s=b[2]+b[3]+b[5]+b[6]
    return (s==4) if center==0 else (s!=2)
def b4s2_delta(ctx:int)->int: return local_delta_from_context(ctx,4,2,B4S2_WEIGHTS)


def local_relator(ctx:int)->np.ndarray:
    bits=[(ctx>>(8-i))&1 for i in range(9)]
    before=np.zeros(32,dtype=int); after=np.zeros(32,dtype=int)
    for c in range(2,7):
        p=0
        for bit in bits[c-2:c+3]: p=(p<<1)|bit
        before[p]+=1
    bits[4]^=1
    for c in range(2,7):
        p=0
        for bit in bits[c-2:c+3]: p=(p<<1)|bit
        after[p]+=1
    return after-before


def global_relator(state:int,n:int,v:int)->np.ndarray:
    before=np.zeros(32,dtype=int); after=np.zeros(32,dtype=int); nxt=flip(state,v)
    for c in range(n):
        before[local_window_int(state,n,c,2)]+=1
        after[local_window_int(nxt,n,c,2)]+=1
    return after-before


def main()->None:
    rule=Rule1D.from_sets({4},{2})
    selected=[ctx for ctx in range(512) if b4s2_legal_context(ctx) and b4s2_delta(ctx)<0]
    assert len(selected)==151
    rows=[local_relator(ctx) for ctx in selected]
    ref=np.array(B4S2_WEIGHTS,dtype=int)
    small_witnesses=[]
    for n in (5,6,7,8):
        for state in range(1<<n):
            moves=legal_moves(state,n,rule)
            if not moves: continue
            good=[]
            for v in moves:
                row=global_relator(state,n,v); d=int(row@ref)
                if d<0: good.append((d,v,row))
            assert good,(n,state)
            d,v,row=min(good); rows.append(row); small_witnesses.append((n,state,v,d))
    A=np.asarray(rows,dtype=float); b=-np.ones(len(rows))
    res=linprog(c=np.zeros(32),A_ub=A,b_ub=b,bounds=[(-20,20)]*32,method='highs')
    if not res.success: raise RuntimeError(res.message)
    x=res.x; worst=float(np.max(A@x))
    print(f"constraints={len(rows)} (151 local + {len(small_witnesses)} small-ring witnesses)")
    print(f"solver max constrained Δ={worst:.12g}")
    print("candidate weights:"); print([round(float(v),8) for v in x])
    assert worst <= -1+1e-8
    scaled=np.rint(3*x).astype(np.int64); exact=A.astype(np.int64)@scaled
    assert np.max(exact) <= -3, int(np.max(exact))
    print(f"scaled integer candidate exact max constrained Δ={int(np.max(exact))} [OK]")
    print("HiGHS found a valid potential for the fixed certified controller [OK]")

if __name__=='__main__': main()
