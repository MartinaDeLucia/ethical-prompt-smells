#!/usr/bin/env python3
"""Reproduce and verify Ethical Prompt Smells replication materials.

Requires Python 3.9+; standard library only. Run from any working directory:
    python3 scripts/reproduce.py

This verifies file integrity, source-data counts, pre-reconciliation agreement,
and independent holdout annotation label agreement. It does not perform
confirmatory LLM response generation or estimate the effects of refactoring.
"""

import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ("None", "Uncertain", "Candidate smell")
SMELLS = tuple(f"EPS-{i:02d}" for i in range(1, 9))


def check(condition, message):
    """Explicit checks remain active if Python is run with -O."""
    if not condition:
        raise ValueError(message)


def read_csv(relative_path):
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        check(reader.fieldnames is not None, f"Empty CSV: {relative_path}")
        rows = list(reader)
    check(all(None not in row for row in rows), f"Malformed CSV rows: {relative_path}")
    return rows


def keyed(rows, name):
    ids = [row["prompt_id"] for row in rows]
    check(len(ids) == len(set(ids)), f"Duplicate prompt_id in {name}")
    return {row["prompt_id"]: row for row in rows}


def verify_checksums():
    """SHA256SUMS.txt covers every regular package file except itself."""
    manifest_path = ROOT / "SHA256SUMS.txt"
    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    expected = {}
    for line in lines:
        check("  " in line, f"Malformed checksum line: {line!r}")
        digest, relative = line.split("  ", 1)
        check(len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest),
              f"Invalid checksum: {relative}")
        check(relative not in expected, f"Duplicate checksum entry: {relative}")
        expected[relative] = digest
    actual_files = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path != manifest_path
    }
    check(set(expected) == actual_files,
          f"Checksum manifest mismatch. Missing: {sorted(actual_files - set(expected))}; "
          f"extraneous: {sorted(set(expected) - actual_files)}")
    for relative, recorded_hash in expected.items():
        actual_hash = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        check(actual_hash == recorded_hash, f"SHA-256 mismatch: {relative}")
    return len(expected)


def cohen_kappa_binary(counts):
    """Return kappa or None if chance agreement is 1 (constant labels)."""
    n = sum(counts.values())
    observed = (counts[("0", "0")] + counts[("1", "1")]) / n
    a0 = (counts[("0", "0")] + counts[("0", "1")]) / n
    b0 = (counts[("0", "0")] + counts[("1", "0")]) / n
    expected = a0 * b0 + (1 - a0) * (1 - b0)
    return observed, None if abs(1 - expected) < 1e-12 else (observed - expected) / (1 - expected)


def main():
    file_count = verify_checksums()

    discovery = read_csv("data/discovery_annotations.csv")
    responses = read_csv("data/sensy_responses.csv")
    prompts = read_csv("data/sensy_prompts.csv")
    families = read_csv("data/reconciliation_families.csv")
    catalog = read_csv("data/catalog_links.csv")
    a1 = read_csv("data/verification_A1.csv")
    a2 = read_csv("data/verification_A2.csv")

    prompt_by_id = keyed(prompts, "sensy_prompts.csv")
    discovery_by_id = keyed(discovery, "discovery_annotations.csv")
    verification1_by_id = keyed(a1, "verification_A1.csv")
    verification2_by_id = keyed(a2, "verification_A2.csv")
    discovery_ids = {pid for pid, row in prompt_by_id.items() if row["partition"] == "discovery"}
    verification_ids = {pid for pid, row in prompt_by_id.items() if row["partition"] == "verification"}

    check(len(prompts) == 321 and len(prompt_by_id) == 321, "Expected 321 distinct SensY prompts")
    check(len(discovery) == 257 and discovery_ids == set(discovery_by_id),
          "Discovery set must contain exactly 257 matching prompt IDs")
    check(len(a1) == len(a2) == 64, "Expected 64 records in each holdout annotation")
    check(verification_ids == set(verification1_by_id) == set(verification2_by_id),
          "Holdout prompt IDs differ between A1, A2, or SensY verification partition")
    check(discovery_ids.isdisjoint(verification_ids) and len(verification_ids) == 64,
          "Discovery and verification partitions must be disjoint")
    check(len(responses) == 2907 and len({r["response_id"] for r in responses}) == 2907,
          "Expected 2,907 distinct SensY responses")
    check({r["prompt_id"] for r in responses} == set(prompt_by_id),
          "Response-to-prompt ID coverage differs from the source corpus")
    check(all(row["prompt_text_verbatim"].strip() for row in prompts), "Blank prompt source text")
    check(all(row["response_text_verbatim"].strip() for row in responses), "Blank response source text")
    inadequate = sum(row["original_adequacy_0_or_1"] == "0" for row in responses)
    check(inadequate == 1460, "Expected 1,460 originally inadequate responses")
    check(len(families) == 16 and len(catalog) == 8,
          "Expected 16 considered mechanism families and eight retained EPSs")

    matrix = Counter((row["A1_label"], row["A2_label"]) for row in discovery)
    check(all(row["A1_label"] in LABELS and row["A2_label"] in LABELS for row in discovery),
          "Unexpected discovery annotation label")
    n = len(discovery)
    matching = sum(matrix[(label, label)] for label in LABELS)
    p_observed = matching / n
    p_expected = sum(
        sum(matrix[(label, other)] for other in LABELS) / n
        * sum(matrix[(other, label)] for other in LABELS) / n
        for label in LABELS
    )
    discovery_kappa = (p_observed - p_expected) / (1 - p_expected)
    check(matching == 170 and abs(discovery_kappa - 0.474437628) < 1e-8,
          "Discovery agreement does not match the registered manuscript")

    assignments = []
    for row in discovery:
        for reviewer in ("A1", "A2"):
            for raw in row[f"{reviewer}_provisional_codes"].split(";"):
                value = raw.strip()
                if value and value.lower() not in {"nessuno", "none", "n/a", "na", "-"}:
                    assignments.append(value)
    distinct_codes = len(set(assignments))
    check(len(assignments) == 315 and distinct_codes == 245,
          "Discovery provisional-code totals differ from source")

    # Compare by stable prompt ID (not row position), and validate all EPS values.
    check(set(verification1_by_id) == set(verification2_by_id), "Holdout A1/A2 ID mismatch")
    expected_columns = {"prompt_id", "sensy_topic", *SMELLS}
    check(set(a1[0]) == expected_columns and set(a2[0]) == expected_columns,
          "Unexpected holdout CSV schema")
    per_smell = {}
    pair_matching = 0
    label_matching = 0
    positives_a1, positives_a2 = {}, {}
    for pid in sorted(verification_ids):
        x, y = verification1_by_id[pid], verification2_by_id[pid]
        check(x["sensy_topic"] == y["sensy_topic"] == prompt_by_id[pid]["sensy_topic"],
              f"Inconsistent source topic for {pid}")
        for row, output in ((x, positives_a1), (y, positives_a2)):
            for smell in SMELLS:
                check(row[smell] in {"0", "1"}, f"Nonbinary {smell} label for {pid}")
            found = [smell for smell in SMELLS if row[smell] == "1"]
            if found:
                output[pid] = found
        if all(x[smell] == y[smell] for smell in SMELLS):
            pair_matching += 1
        label_matching += sum(x[smell] == y[smell] for smell in SMELLS)
    check(positives_a1 == positives_a2 == {"P0343": ["EPS-02"], "P0352": ["EPS-02"]},
          "Holdout positives differ from the manuscript: two EPS-02 prompts expected")
    check(pair_matching == 64 and label_matching == 512,
          "Holdout labeling agreement differs from the reported complete agreement")

    for smell in SMELLS:
        counts = Counter(
            (verification1_by_id[pid][smell], verification2_by_id[pid][smell])
            for pid in verification_ids
        )
        observed, kappa = cohen_kappa_binary(counts)
        per_smell[smell] = (counts, observed, kappa)

    print(f"SHA-256 integrity: PASS ({file_count} files listed and verified)")
    print(f"SensY selection: {len(prompts)} distinct prompts; {len(responses)} responses; "
          f"{inadequate} originally inadequate")
    print("Discovery: 257 prompts; holdout: 64; disjoint partitions")
    print("Pre-reconciliation discovery contingency (A1 rows, A2 columns):")
    print("                  " + "".join(f"{label:>19}" for label in LABELS))
    for first in LABELS:
        print(f"{first:>18}" + "".join(f"{matrix[(first, second)]:>19}" for second in LABELS))
    print(f"Discovery agreement: {matching}/{n} ({p_observed:.2%}); Cohen's kappa = {discovery_kappa:.8f}")
    print(f"Provisional-code assignments: {len(assignments)}; distinct codes: {distinct_codes}")
    print("Reconciliation: 16 documented mechanism families; 8 retained EPSs "
          "(not discovery prevalence counts)")
    print("Holdout: 64 prompts independently labeled in files A1 and A2")
    print(f"Exact-match prompt agreement: {pair_matching}/64 ({pair_matching/64:.2%})")
    print(f"Binary EPS-label agreement: {label_matching}/512 ({label_matching/512:.2%})")
    print("Per-smell holdout agreement (positives A1/A2; observed agreement; Cohen's kappa):")
    for smell in SMELLS:
        counts, observed, kappa = per_smell[smell]
        pos1 = counts[("1", "0")] + counts[("1", "1")]
        pos2 = counts[("0", "1")] + counts[("1", "1")]
        kappa_text = "undefined (no label variation)" if kappa is None else f"{kappa:.6f}"
        print(f"  {smell}: {pos1}/{pos2}; {observed:.2%}; {kappa_text}")
    print("Agreed positive holdout prompts: P0343 and P0352 (EPS-02 only)")
    print("Note: agreement on all-negative categories does not validate positive-case recognition;")
    print("      independence of annotations cannot be established from matching CSV labels alone.")
    print("CATALOG DATA AND INTEGRITY CHECKS: PASS")


if __name__ == "__main__":
    main()
