#!/usr/bin/env python3
"""Calculate EA×RF *independence-product approximations* from reported marginals.

CAUTION: This is not a direct joint simulation of EA and RF, nor a CLMM power
calculation. Values are transcribed historical marginal estimates. By default
no derived output file is written into the repository (to preserve checksums).
"""
import argparse
import csv
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
INPUT = HERE / 'reported_marginal_powers.csv'


def compute(rows):
    by_key = {(int(r['prompt_pairs']), float(r['tau']), r['scenario']): float(r['power_reported']) for r in rows}
    output = []
    for pairs in (20,40,60):
        for tau in (0.0,0.5):
            for ea in ('EA_OR1.5','EA_OR2'):
                for rf in ('RF_OR1_vs_2/3','RF_OR0.9_vs_2/3'):
                    p_ea, p_rf = by_key[(pairs,tau,ea)], by_key[(pairs,tau,rf)]
                    output.append(dict(prompt_pairs=pairs, tau=tau,
                        EA_scenario=ea, RF_scenario=rf, EA_marginal=p_ea,
                        RF_marginal=p_rf, product_independence_approx=round(p_ea*p_rf,6),
                        status='calculated_from_rounded_reported_marginals_NOT_direct_joint'))
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=pathlib.Path,help='Optional destination for derived CSV (outside repository recommended)')
    a = p.parse_args()
    with INPUT.open(newline='', encoding='utf-8') as f:
        results = compute(list(csv.DictReader(f)))
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        with a.out.open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
        print('Saved derived table:', a.out)
    for r in results:
        if r['prompt_pairs']==60 and r['tau']==0.5 and r['RF_scenario']=='RF_OR1_vs_2/3':
            print(f"{r['EA_scenario']}, RF OR 1, N 60, tau .5: independence-product approximation {r['product_independence_approx']:.4f}")

if __name__ == '__main__': main()
