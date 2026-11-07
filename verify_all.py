#!/usr/bin/env python3
"""Run fast available Stage-1 checks; NEVER executes the Stage-2 experiment."""
from pathlib import Path
import os, subprocess, sys
ROOT=Path(__file__).resolve().parent

def run(*args):
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    print('\n>>>', ' '.join(args),flush=True)
    subprocess.run([sys.executable,*args],cwd=ROOT,check=True,env=env)

if __name__ == '__main__':
    run('verify_sha256.py')
    run('01_catalog/scripts/reproduce.py')
    run('-m','unittest','discover','-s','tests','-p','test_*.py','-v')
    print('\nAvailable Python Stage-1 checks PASSED. Historical power results are not exactly replayed; no confirmatory CLMM is fitted.')
