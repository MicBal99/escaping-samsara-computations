from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class ReproducibilityScripts(unittest.TestCase):
    def run_script(self,name:str):
        env=os.environ.copy(); env['PYTHONPATH']=str(ROOT)
        subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)

    def test_method1_1d(self): self.run_script('verify_method1_1d.py')
    def test_method1_2d(self): self.run_script('verify_method1_2d.py')
    def test_method2(self): self.run_script('verify_method2.py')
    def test_method3(self): self.run_script('verify_method3.py')


if __name__=='__main__': unittest.main()
