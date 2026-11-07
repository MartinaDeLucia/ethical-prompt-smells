#!/usr/bin/env python3
"""Capped stratified sampling following Section VI of the reference manuscript.

Input CSV has exactly one human-validated prompt pair per ID, with columns:
    prompt_id,smell
where smell is one of EPS-01 ... EPS-08.
Do not use this script on candidates that have not passed independent pair validation.

Decision: if sum(n_s) >= N, choose minimal integer C with sum(min(n_s,C)) >= N.
Strata with n_s <= C contribute all pairs; larger strata contribute C uniform
random draws without replacement. N is a target, not always the exact sample size.
If fewer than N available, select all and set sensitivity flag.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

SMELLS = [f'EPS-{i:02d}' for i in range(1,9)]


def select_pairs(rows, *, N=60, seed=20261106):
    if type(N) is not int or N < 1:
        raise ValueError('N must be a positive integer')
    groups = {smell: [] for smell in SMELLS}
    seen=set()
    for row in rows:
        pid=str(row.get('prompt_id','')).strip(); smell=str(row.get('smell','')).strip()
        if not pid or smell not in SMELLS:
            raise ValueError(f'Invalid prompt_id or smell: {row!r}')
        if pid in seen:
            raise ValueError(f'Duplicate prompt_id: {pid}')
        seen.add(pid)
        groups[smell].append({'prompt_id':pid,'smell':smell})
    for k in SMELLS:
        groups[k].sort(key=lambda a:a['prompt_id'])
    counts={s:len(groups[s]) for s in SMELLS}
    total=sum(counts.values())
    if total == 0:
        raise ValueError('No validated pairs provided')
    if total < N:
        C=None
        selected=[r for smell in SMELLS for r in groups[smell]]
    else:
        C=next(c for c in range(1,max(counts.values())+1)
               if sum(min(n,c) for n in counts.values()) >= N)
        rng=random.Random(seed)
        selected=[]
        for smell in SMELLS:
            candidates=groups[smell]
            chosen=candidates if len(candidates)<=C else rng.sample(candidates,C)
            selected.extend(sorted(chosen,key=lambda r:r['prompt_id']))
    summary={
        'N': N, 'C':C, 'seed':seed, 'total_available':total,
        'total_selected':len(selected), 'sensitivity_analysis_required':total<N,
        'eligible_validated_by_smell': counts,
        'selected_by_smell':dict(sorted(Counter(r['smell'] for r in selected).items())),
        'sampling_rule':'min_C_with_sum_min_ns_C_ge_N_if_enough_else_all',
        'data_type':'human_validated_pairs_only_not_raw_prompts',
    }
    if C is not None:
        assert len(selected) >= N
        assert sum(min(v,C) for v in counts.values())==len(selected)
        assert sum(min(v,C-1) for v in counts.values())<N
    else:
        assert len(selected)==total
    return selected,summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('validated_csv',type=Path)
    p.add_argument('--N',type=int,default=60)
    p.add_argument('--seed',type=int,default=20261106)
    p.add_argument('--out',type=Path,default=Path('sampling_output'))
    a=p.parse_args()
    with a.validated_csv.open('r',encoding='utf-8-sig',newline='') as f:
        source=list(csv.DictReader(f))
    chosen,meta=select_pairs(source,N=a.N,seed=a.seed)
    meta['input_file_sha256']=hashlib.sha256(a.validated_csv.read_bytes()).hexdigest()
    a.out.mkdir(parents=True,exist_ok=True)
    with (a.out/'selected_pairs.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['prompt_id','smell']);w.writeheader();w.writerows(chosen)
    (a.out/'sampling_summary.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta,indent=2))

if __name__=='__main__':main()
