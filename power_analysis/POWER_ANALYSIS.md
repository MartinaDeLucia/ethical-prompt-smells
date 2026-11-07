# Preliminary simulation-based power analysis — Stage 1

This directory documents **preliminary planning results**, not the analysis of observed experimental outcomes. The manuscript is the authority for the preregistered design and hypothesis thresholds.

## Original simulation

`preliminary_simulation.py` is the unchanged supplied program underlying the preliminary power exploration. It simulates ordinal scores (five categories), three generating model families, two prompt conditions and three repetitions per model and condition. It considers 20, 40 and 60 prompt pairs, a prompt intercept SD of 1.0, prompt-by-model SD of 0.7, prompt-specific condition-effect SD (`tau`) of 0 or 0.5, model shifts 0/+0.3/-0.3, and latent ordinal thresholds -1.5/-0.5/0.5/1.5. Scenarios include EA odds ratios 1.5 and 2, and RF odds ratios 1 and 0.9 against the non-inferiority margin 2/3. The reported preliminary estimates were based on 150 replications per scenario.

**Important estimator distinction:** the program fits a cumulative-odds model with *prompt fixed effects* and cluster-based OPG sandwich standard errors. It does **not** fit the prompt-random-intercept/random-condition-slope CLMMs specified for confirmatory inference in Section VII. Separate EA and RF outcomes were simulated; joint rejection was **not** directly simulated.

## Reported planning figures

`reported_marginal_powers.csv` contains marginal power estimates transcribed from the earlier preliminary report. `joint_from_marginals.py` calculates their product, assuming independence of EA and RF *test-rejection events*. With 60 pairs, tau=0.5 and RF OR=1:

| EA OR | Marginal EA | Marginal RF | Product approximation |
| --- | ---: | ---: | ---: |
| 2.0 | 1.00 | 0.91 | **0.91** (about 91%) |
| 1.5 | 0.85 | 0.91 | **0.7735** (about 77%) |

For EA OR=2, RF OR=0.9, the same assumptions yield about 66%. These are conditional approximations, **not** empirical joint power estimates and **not** a guarantee that 60 pairs provide 80% power under all plausible effects.

Run (standard library only):

```bash
python power_analysis/joint_from_marginals.py
```

To export a derived table, specify a destination outside the immutable deposit:

```bash
python power_analysis/joint_from_marginals.py --out /tmp/eps_joint_approx.csv
```

## Re-running the original program

The source simulator requires the dependencies listed in `requirements.txt` (NumPy and SciPy). Run it from a separate working directory, because the original program writes `results.json` to the current directory. For example, from a new temporary working directory, execute `python /absolute/path/to/power_analysis/preliminary_simulation.py 150`. This may be computationally expensive and depends on multiprocessing support.

**Exact historical reproduction is not claimed.** The program uses Python's process-dependent `hash()` in seed construction; the historical seed state and per-replicate results are unavailable. Its optimization/convergence behavior also needs attention if it is reused. New simulation output must be identified as a new run, not substituted silently for the manuscript's historical marginal estimates. At approximately 80% power, 150 replications imply about 3.3 percentage points of Monte Carlo standard error.

## If fewer than N=60 validated pairs are available

Under the manuscript, all eligible validated pairs will then be retained, and **a pre-generation sensitivity analysis at 80% joint power will be reported** without altering the hypotheses, non-inferiority margin, or significance levels. That prospective analysis is **not** represented as implemented by the deposited preliminary simulator. Its final method and results must be documented before confirmatory generation if this branch is reached.
