# Submission Validation Protocol & Validator Integration

This document describes the validation protocol, error checks, and verification procedures executed before submitting predictions to the Amazon ML Challenge leaderboard.

---

## 1. Official Challenge Validator

The competition provides an official validator script located at:
`student_resource/utils/validate_submission.py`

This script executes deep structural, format, cardinality, and ID domain checks across both output files:
- `output/matching_results.tsv`
- `output/candidate_pairs.tsv`

---

## 2. Validation Execution Command

To run validation:

```bash
python3 student_resource/utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir student_resource/dataset/test
```

### Full Verification Log

```text
Reading test source1 IDs...
Read 1732544 IDs from test source1.
Reading valid candidate IDs (source2 and source3)...
Read 10000000 valid candidate IDs.
Validating candidate_pairs.tsv: output/candidate_pairs.tsv
1732544 lines checked.
Validating matching_results.tsv: output/matching_results.tsv
1732544 lines checked.
Checking candidate coverage...
1732544 lines checked.

Summary:
Total issues: 0 (0 blocking, 0 warnings)
Status: PASS — no blocking issues found. Safe to submit.
```

---

## 3. Comprehensive Check Inventory

The validator verifies the following conditions:

| Check Category | Verification Details | Our Pipeline Status |
| :--- | :--- | :---: |
| **File Existence** | Both `candidate_pairs.tsv` and `matching_results.tsv` exist in the target path. | **PASS** |
| **TSV Format** | Files are strictly tab-separated (`\t`), UTF-8 encoded, with exact headers. | **PASS** |
| **Header Names** | `source1_entity_id\tcandidate_entity_ids` and `source1_entity_id\tmatched_entity_ids`. | **PASS** |
| **Row Count** | Exactly $1,732,544$ lines matching test Source 1 row count. | **PASS** |
| **ID Alignment** | Every `source1_entity_id` matches the exact test entity IDs and order. | **PASS** |
| **Target ID Domain** | All matched and candidate IDs exist in `test_source2` or `test_source3`. | **PASS** |
| **Self-Match Check** | No `source1_` entity appears in candidate or match columns. | **PASS** |
| **Subset Invariant** | Every predicted match is present in the corresponding candidate set: $\text{matches} \subseteq \text{candidates}$. | **PASS** |
| **Singleton Format** | Unmatched entities have empty string representation (`""`) after the tab. | **PASS** |

---

## 4. Automated Integration Test

To guarantee that validation cannot regress, our test suite includes an automated integration test (`tests/test_pipeline.py::test_end_to_end_pipeline_and_official_validator`) that generates mock TSVs, runs the pipeline, calls the validator script via Python subprocess, and asserts a return code of `0`.
