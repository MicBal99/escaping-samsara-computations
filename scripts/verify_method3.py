#!/usr/bin/env python3
from __future__ import annotations
from itertools import combinations
from escaping_samsara.one_d import MOVE_TYPES, Rule1D, flip, legal_at, move_type_at

def popcount(x:int)->int: return x.bit_count()
def types_in_state(state:int,n:int)->set[str]: return {move_type_at(state,n,v) for v in range(n)}
def hull(C:set[int],n:int)->set[str]:
    safe=set(MOVE_TYPES)
    for typ in MOVE_TYPES:
        for x in C:
            for v in range(n):
                if move_type_at(x,n,v)==typ and flip(x,v) not in C:
                    safe.discard(typ); break
            if typ not in safe: break
    return safe
def is_activity_kernel(K:set[str],C:set[int],n:int)->bool: return all(K & types_in_state(x,n) for x in C)
def minimal_safe_kernels(C:set[int],n:int,U:set[str])->list[set[str]]:
    elems=sorted(U)
    for size in range(len(elems)+1):
        out=[]
        for comb in combinations(elems,size):
            K=set(comb)
            if is_activity_kernel(K,C,n): out.append(K)
        if out: return out
    return []
def budget_to_rule(L:set[str])->Rule1D:
    B={i for i in range(5) if f"b{i}" in L}; S={i for i in range(5) if f"d{i}" not in L}; return Rule1D.from_sets(B,S)
def verify_six_state_interval()->None:
    n=5; C0={x for x in range(1<<n) if popcount(x)<=1}; assert len(C0)==6; U=hull(C0,n); assert U==set(MOVE_TYPES)-{"b1"}
    kernels=minimal_safe_kernels(C0,n,U); assert {"b0","d0"} in kernels; assert 2**(len(U)-2)==128
    print("Method III C0: |C0|=6, U(C0)=M\\{b1}, minimal kernel {b0,d0}, interval size 128 [OK]")
def verify_union_interval()->None:
    n=5; C0={x for x in range(1<<n) if popcount(x)<=1}; C1={x for x in range(1<<n) if 1<=popcount(x)<=2}; C=C0|C1; assert len(C)==16
    U=hull(C,n); assert U==set(MOVE_TYPES)-{"b2"}; K={"b0","b1","d1"}; assert K<=U and is_activity_kernel(K,C,n); assert 2**(len(U)-len(K))==64
    L={"b0","b1","d0","d1"}; rule=budget_to_rule(L); assert rule.B==frozenset({0,1}) and rule.S==frozenset({2,3,4})
    def has_escape(Cset:set[int],typ:str)->bool: return any(move_type_at(x,n,v)==typ and flip(x,v) not in Cset for x in Cset for v in range(n))
    assert has_escape(C0,"b1") and has_escape(C1,"d0")
    print("Method III union: U(C)=M\\{b2}, kernel {b0,b1,d1}, interval size 64, B01/S234 example [OK]")
def verify_base_samsara()->None:
    n=5; rule=Rule1D.from_sets({0},{1,2,3,4}); C={x for x in range(1<<n) if popcount(x)<=1}
    for x in C:
        legal=[v for v in range(n) if legal_at(x,n,v,rule)]; assert legal; assert all(flip(x,v) in C for v in legal)
    print("Method III six-state B0/S1234 closed moving region [OK]")
def main()->None: verify_base_samsara(); verify_six_state_interval(); verify_union_interval()
if __name__=='__main__': main()
