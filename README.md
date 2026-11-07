# Ethical Prompt Smells — Stage 1 Replication Package

**Manuscript:** *The Ethical Dimension of Prompt Smells: A Catalog and Impact Assessment on LLM Responses*  
**Authors:** Martina De Lucia, Alessandra Raia, Andrea De Lucia, Fabio Palomba  
**Submission:** SANER 2027 Registered Reports — Stage 1

## Scope

This deposit supports the completed **elicitation and preliminary independent application of eight Ethical Prompt Smells (EPSs)** and documents computational materials for the *planned* confirmatory paired experiment. It contains actual historical corpus selections, human annotation records, catalog material, and preliminary power-analysis source code, plus the preregistered sampling algorithm and **proposed** research-authored LLM prompts.

**It contains no Stage-2 screening results, validated prompt pairs, generated experimental responses, human calibration scores, EA/RF outcome scores, or confirmatory model fits.** The submitted manuscript—not this README—is authoritative for the registered hypotheses and procedures. Files representing future experimental inputs are not observed results.

## Contents

| Location | Purpose | Status |
| --- | --- | --- |
| `01_catalog/` | 321 selected SensY prompts, 2,907 linked responses, discovery and verification annotations, reconciliation families, codebook, reproducibility checks | **Completed empirical materials** |
| `power_analysis/` | Original preliminary simulation, transcribed marginal power results and independently computed product approximations | **Historical planning analysis** |
| `sampling/` | Tested implementation of smallest-cap EPS-stratified sampling (target N=60) | **Prospective procedure** |
| `supplementary_appendix/` | Canonical research-authored refactoring, generation and separate EA/RF evaluation templates | **Proposed, subject to pilot calibration** |
| `tests/` | Unit tests of the sampling algorithm and marginal-product calculation | **Software verification only** |

The input/output schemas are documented in the scripts and adjacent explanations. No empty outcome-record templates, synthetic experimental dataset, or untested confirmatory CLMM program is included.

## Reproduce deposited Stage-1 checks

Python **3.10 or later** (standard library only for the command below) is sufficient. From the extracted repository root:

```bash
python verify_all.py
```

This checks all distributed-file SHA-256 digests, the nested catalog evidence manifest, the reported catalog totals and annotation agreement, and the automated sampling/power-arithmetic tests.

| Check | Deposited records |
| --- | ---: |
| Selected prompts and linked original responses | 321 / 2,907 |
| Originally inadequate responses | 1,460 |
| Discovery / holdout prompts | 257 / 64 |
| Discovery annotation agreement | 170/257 (66.15%) |
| Discovery Cohen's kappa | approximately 0.4744 |
| Distinct provisional codes | 245 |
| Independent holdout agreement | 64/64 |
| Holdout positive EPS instances | two, both EPS-02 |

Run the empirical data check alone with `python 01_catalog/scripts/reproduce.py` or the Python tests with `python -m unittest discover -s tests -v`. These checks substantiate the deposited counts, **not** the chronology or independence of the historical human work.

## Inspect the preliminary power analysis

```bash
python power_analysis/joint_from_marginals.py
```

This derives the manuscript's **approximately 91% and 77%** planning-power figures at N=60 under the indicated scenarios by multiplying **previously reported marginal powers**. These are *independence-product approximations*, not direct simulated joint power for the planned CLMMs. The historical scenario outputs cannot be reproduced bit-for-bit: the original simulator employs a process-dependent seed construction and original replicate-level output was not supplied. Read [`power_analysis/POWER_ANALYSIS.md`](power_analysis/POWER_ANALYSIS.md) before interpreting the results. Installing `requirements.txt` is needed **only** to re-run the original NumPy/SciPy-based simulator, which is computationally demanding and produces a new run.

## Planned experimental procedure

The manuscript (Sections VI–VII) specifies: independent EPS screening; Gemma 4 31B IT-assisted refactoring; independent two-person pair validation with at most one revision; capped EPS-stratified selection (scenario-dependent target 60); response generation with GPT, Claude and Qwen, three times for each model/pair/condition; blinded separate 1–5 EA and RF evaluations using a JudgeBench-selected LLM judge; and confirmatory tests using separate proportional-odds CLMMs. Detailed prompt inputs are indexed in [`supplementary_appendix/PROMPT_DESIGN_APPENDIX.md`](supplementary_appendix/PROMPT_DESIGN_APPENDIX.md).

The statistical decision rule is defined in the manuscript: two separate one-sided tests at alpha 0.025; the joint claim requires both the EA superiority limit (odds ratio >1) and RF non-inferiority limit (odds ratio >2/3). These **future analyses have not been performed or validated on confirmatory results**. If fewer than 60 eligible validated pairs are available, the manuscript calls for all to be retained and for sensitivity power to be reported before response generation; no completed sensitivity analysis is deposited.

## Data source and evidence limitations

Source data originate from SensY, cited in the manuscript as G. Voria et al., *Bias Ahead: Sensitive Prompts as Early Warnings for Fairness in Large Language Models* (SANER-C 2026). The original publication identifies the upstream dataset; this deposit includes the 321 study-selected prompts and associated responses, **not** the full pool that will be screened in Stage 2. The version and IDs of any additional retrieved upstream records must be documented when Stage 2 is executed.

The `01_catalog/documentation/CODEBOOK.md` is an English rendering of the approved codebook. The deposited annotation records and 16 reconciliation families document the reported counts and category-level decisions; they do not independently authenticate the historical codebook freeze date, reproduce the original stratified random split from its seed, or provide a complete individual mapping of all provisional codes to final EPSs. No undocumented decisions have been reconstructed for this package.

**Public-sharing check:** the source records may contain sensitive user text and third-party model responses. Before making the archive publicly downloadable, the study authors must verify any redistribution permissions, privacy constraints and applicable dataset terms. Presence in this archive is not a license grant.

## Integrity and intended interpretation

`SHA256SUMS.txt` lists every supplied file except itself; `verify_sha256.py` enforces its exact inventory. The `01_catalog/SHA256SUMS.txt` preserves an independent checksum manifest of the deposited catalog materials. After any permitted update, regenerate the affected manifests and rerun `python verify_all.py` from a fresh extraction.

This is a **Stage-1 evidence-and-materials deposit**, not an executable end-to-end Stage-2 experiment or a completed confirmatory replication. The experiment and its analysis outputs belong to Stage 2.
