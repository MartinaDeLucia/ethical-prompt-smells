# Supplementary Appendix — Proposed Experimental Prompt Templates

**Companion to:** *The Ethical Dimension of Prompt Smells: A Catalog and Impact Assessment on LLM Responses* (SANER 2027 Registered Report, Stage 1).

**Status:** prospective materials only; no confirmatory response generation or evaluation has yet been performed. The exact instructions may require pilot calibration/finalization before execution as specified in the manuscript. Their inclusion does not imply empirical validation.

The files in [`templates/`](templates/) are the **canonical research-authored messages and payloads**. This index does not duplicate their complete text. Template placeholders in `{{DOUBLE_BRACES}}` must be replaced with actual values and correctly serialized before use; JSON-like template files are not filled inputs.

| File | Function | Role / transmitted? |
| --- | --- | --- |
| `R01_refactoring_system.txt` | First proposal: remove one identified EPS while preserving original intent | Refactoring system message |
| `R02_refactoring_user.json.tmpl` | Original prompt, targeted EPS and frozen codebook entry | Refactoring user payload |
| `R03_refactoring_revision_system.txt` | Revises a candidate after human feedback | Revision system message |
| `R04_refactoring_revision_user.json.tmpl` | Previous candidate and documented feedback | Revision user payload |
| `G01_response_generation_instructions.txt` | Verbatim raw prompt submission and generation controls | **Documentation only; not sent** |
| `E00_judge_system.txt` | Common blinded single-response evaluation | Judge system message |
| `E01_ethical_adequacy_user.txt` | EA-specific ordinal 1–5 rubric and input | Judge user message |
| `E02_request_fulfillment_user.txt` | RF-specific ordinal 1–5 rubric and input | Judge user message |

## Connection to registered procedure

- **Eligibility:** each prompt is screened against the eight-EPS codebook; only exactly-one-EPS prompts are candidates for refactoring. The codebook is in `../01_catalog/documentation/CODEBOOK.md`.
- **Refactoring:** the paper specifies Gemma 4 31B IT. The target EPS definition plus its inclusion/exclusion rules and original prompt are provided. LLM proposals do not establish eligibility. Two human evaluators independently assess removal, intent preservation, and unrelated modifications/new EPSs; disagreements are discussed. **At most one revision and reassessment** is permitted before excluding a failing pair.
- **Sampling:** only validated pairs enter the capped EPS-stratified selection (target N=60), implemented in `../sampling/capped_sampling.py`.
- **Generation:** the registered response-generator families are GPT, Claude and Qwen; there are three generations **per model, pair and condition**, with fresh sessions and randomized condition order. Temperature is 0.7, top-p is 1.0, output limit is 2,048 tokens, and top-k is left at the provider default. Unsupported options and actual model version IDs must be documented. G01 is an operational record of input construction, not an extra system message.
- **Evaluation:** the judge is chosen at execution time by the paper's JudgeBench rule; scores for **EA** and **RF** are separate 1–5 ordinal outcomes, both evaluated against the **original prompt**, with no explicit condition/model identifiers supplied to the judge. Rubrics are proposed until the prespecified calibration and reliability checks have been completed. One response is evaluated at a time.
- **Statistical inference:** the paper specifies two separate proportional-odds CLMMs with prompt random intercepts and condition slopes and fixed effects for condition, model family and smell. A joint confirmatory success requires both EA superiority and RF non-inferiority at one-sided alpha 0.025. No confirmatory outcomes or fitted models are supplied at Stage 1.

This appendix defines experimental *inputs*, not a program for executing third-party APIs, a data-collection sheet, or a claim that screening, calibration, judge selection, or model freezing has already occurred.
