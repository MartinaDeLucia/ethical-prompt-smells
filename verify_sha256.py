#!/usr/bin/env python3
"""Verify the merged Stage-1 package; no third-party dependencies."""
from pathlib import Path
import hashlib
ROOT = Path(__file__).resolve().parent
EXCLUDE = {'SHA256SUMS.txt'}

def valid(path):
    return path.is_file() and not any(part in {'.git', '__pycache__'} for part in path.relative_to(ROOT).parts) and path.suffix != '.pyc' and path.relative_to(ROOT).as_posix() not in EXCLUDE

def verify():
    manifest = ROOT/'SHA256SUMS.txt'
    expected={}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        digest, rel = line.split('  ',1)
        if rel in expected: raise ValueError('Duplicate checksum: '+rel)
        expected[rel]=digest
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if valid(p)}
    if actual != set(expected):
        raise RuntimeError('File inventory mismatch: missing from manifest '+str(sorted(actual-set(expected)))+'; obsolete '+str(sorted(set(expected)-actual)))
    for rel,digest in expected.items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Checksum mismatch: '+rel)
    print(f'Full repository SHA-256: PASS ({len(expected)} files verified)')

if __name__ == '__main__': verify()
