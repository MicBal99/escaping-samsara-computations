#!/usr/bin/env python3
from __future__ import annotations

from escaping_samsara.graphs import strongly_connected_components
from escaping_samsara.certificates import B4S2_RADIUS2_WEIGHTS, B12S12_RADIUS1_WEIGHTS
from escaping_samsara.one_d import Rule1D, additive_window_potential, flip, legal_at, legal_moves, local_delta_from_context, move_type_at, state_from_bits, word_to_int

B4S2_WEIGHTS=B4S2_RADIUS2_WEIGHTS
B12S12_WINDOW_WEIGHTS=B12S12_RADIUS1_WEIGHTS

def w3(p:int)->int: return B12S12_WINDOW_WEIGHTS.get(p,0)
def delta_b12s12_context5(ctx:int)->int:
    bits=[(ctx>>(4-i))&1 for i in range(5)]
    before=w3(word_to_int(bits[0:3]))+w3(word_to_int(bits[1:4]))+w3(word_to_int(bits[2:5]))
    bits[2]^=1
    after=w3(word_to_int(bits[0:3]))+w3(word_to_int(bits[1:4]))+w3(word_to_int(bits[2:5]))
    return after-before

def legal_context5(ctx:int,rule:Rule1D)->bool:
    bits=[(ctx>>(4-i))&1 for i in range(5)]; center=bits[2]; s=bits[0]+bits[1]+bits[3]+bits[4]
    return (s in rule.B) if center==0 else (s not in rule.S)

def verify_b12s12()->None:
    rule=Rule1D.from_sets({1,2},{1,2}); by_type={}
    for ctx in range(32):
        if not legal_context5(ctx,rule): continue
        bits=[(ctx>>(4-i))&1 for i in range(5)]; center=bits[2]; s=bits[0]+bits[1]+bits[3]+bits[4]; typ=("b" if center==0 else "d")+str(s)
        by_type.setdefault(typ,set()).add(delta_b12s12_context5(ctx))
    expected={"b1":{-3},"b2":{-1},"d0":{5},"d3":{-1},"d4":{-3}}; assert by_type==expected,by_type
    print("B12/S12 local Δ table:",{k:next(iter(v)) for k,v in sorted(by_type.items())},"[OK]")
    words=["1001100","0001100","0101100","0101110","0100110","0000110","1000110","1001110","1001100"]
    states=[state_from_bits([int(c) for c in w]) for w in words]
    for a,b in zip(states,states[1:]):
        diff=a^b; assert diff and diff&(diff-1)==0; v=diff.bit_length()-1; assert legal_at(a,7,v,rule)
    types=[move_type_at(a,7,(a^b).bit_length()-1) for a,b in zip(states,states[1:])]; assert types.count("d0")==2
    print("B12/S12 explicit N=7 cycle move types:",types,"[OK]")

def context9_bits(ctx:int)->list[int]: return [(ctx>>(8-i))&1 for i in range(9)]
def b4s2_legal_context(ctx:int)->bool:
    b=context9_bits(ctx); center=b[4]; s=b[2]+b[3]+b[5]+b[6]; return (s==4) if center==0 else (s!=2)
def b4s2_delta(ctx:int,weights=B4S2_WEIGHTS)->int: return local_delta_from_context(ctx,4,2,weights)
def verify_b4s2_local_and_cover()->None:
    illegal=[]; decreasing=[]; nondecreasing=[]
    for ctx in range(512):
        if not b4s2_legal_context(ctx): illegal.append(ctx)
        elif b4s2_delta(ctx)<0: decreasing.append(ctx)
        else: nondecreasing.append(ctx)
    assert (len(illegal),len(decreasing),len(nondecreasing))==(336,151,25)
    print("B4/S2 context census: 336 illegal, 151 legal decreasing, 25 legal non-decreasing [OK]")
    allowed=set(decreasing); vertices=list(range(256)); adjacency={v:[] for v in vertices}; residual=[]
    for ctx in range(512):
        if ctx in allowed: continue
        u=ctx>>1; v=ctx&0xFF; adjacency[u].append(v)
        if b4s2_legal_context(ctx): residual.append((ctx,u,v))
    comps=strongly_connected_components(vertices,adjacency); cid={v:i for i,c in enumerate(comps) for v in c}
    bad=[ctx for ctx,u,v in residual if cid[u]==cid[v]]; assert len(residual)==25 and not bad
    print("B4/S2 de Bruijn Cover test: 25 residual legal edges, 0 on directed cycles [OK]")
def global_delta(state:int,n:int,v:int)->int:
    return additive_window_potential(flip(state,v),n,2,B4S2_WEIGHTS)-additive_window_potential(state,n,2,B4S2_WEIGHTS)
def verify_b4s2_small_rings()->None:
    rule=Rule1D.from_sets({4},{2}); total=0
    for n in (5,6,7,8):
        for state in range(1<<n):
            moves=legal_moves(state,n,rule)
            if moves: assert any(global_delta(state,n,v)<0 for v in moves)
            total+=1
    assert total==480; print("B4/S2 direct small-ring CLF check: 480 configurations for N=5..8 [OK]")
def verify_b4s2_radius1_obstruction()->None:
    rule=Rule1D.from_sets({4},{2})
    for word,expected in [("110110",{"b4"}),("111111",{"d4"})]:
        state=state_from_bits([int(c) for c in word]); types={move_type_at(state,6,v) for v in legal_moves(state,6,rule)}; assert types==expected
    print("B4/S2 N=6 radius-1 obstruction configurations [OK]")
def main()->None:
    verify_b12s12(); verify_b4s2_radius1_obstruction(); verify_b4s2_local_and_cover(); verify_b4s2_small_rings()
if __name__=='__main__': main()
