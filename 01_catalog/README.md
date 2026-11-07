# Ethical Prompt Smell catalog — empirical evidence (Section III)

The `data/` directory contains the study-selected SensY prompt/response records, two-annotator discovery labels, independent verification labels, and reconciliation records. `documentation/CODEBOOK.md` describes the eight EPS types, their inclusion/exclusion criteria, examples, and boundary cases.

To verify the deposited data and reproduce the reported counts and agreement statistics from the repository root:

```bash
python 01_catalog/scripts/reproduce.py
```

This command checks local SHA-256 integrity, 321 prompts, 2,907 source responses, discovery/verification partitions (257/64), 245 distinct provisional codes, and annotation agreement (including Cohen's kappa). The full upstream sensitive SensY pool for future screening is **not** included; consult the cited SensY publication for its source and access conditions. The checks do not independently demonstrate the timing of human decisions or codebook freeze.
