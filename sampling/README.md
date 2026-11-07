# Capped stratified sampling (manuscript Section VI)

The algorithm is provided for the **future confirmatory experiment** and has been unit-tested with synthetic rows. No validated confirmatory pairs are included here.

Input CSV: one independently validated prompt pair per row, with columns `prompt_id,smell` and exactly one smell (`EPS-01` through `EPS-08`). The 257 discovery prompts must not be used as confirmatory subjects. Screening and human validation are prerequisites to this script.

If at least `N=60` validated pairs exist, choose the smallest positive integer `C` for which `sum(min(n_s, C) for s in EPS01..EPS08) >= N`. Keep all from strata with `n_s <= C` and uniformly subsample `C` without replacement from larger strata. The total selected can exceed N. If fewer than N pairs exist, select all and flag the preregistered pre-generation sensitivity analysis. Record seed, `C`, per-smell counts, selected IDs and source checksum.

Run on actual **validated** input (supplied only after prospective screening):

```bash
python sampling/capped_sampling.py path/to/validated_pairs.csv --N 60 --seed 20261106 --out /path/to/output
```

The script is deterministic for a fixed seed and input set. To verify its implementation without real Stage-2 records, use `python -m unittest discover -s tests -v` from the repository root. This produces no fake confirmatory evidence.
