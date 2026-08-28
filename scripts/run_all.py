#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

VERIFY=[
    'verify_method1_1d.py',
    'verify_method1_2d.py',
    'verify_method2.py',
    'verify_method3.py',
]
SOLVE=[
    'solve_method1_1d.py',
    'solve_method1_2d.py',
    'solve_method2_b4s2.py',
]


def run(name:str)->None:
    env=os.environ.copy()
    env['PYTHONPATH']=str(ROOT)+os.pathsep+env.get('PYTHONPATH','')
    print(f"\n=== {name} ===",flush=True)
    subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,env=env,check=True)


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--solvers',action='store_true',help='also re-run the LP discovery/re-solving scripts')
    args=ap.parse_args()
    for name in VERIFY: run(name)
    if args.solvers:
        for name in SOLVE: run(name)
    print('\nALL REQUESTED CHECKS PASSED')

if __name__=='__main__': main()
