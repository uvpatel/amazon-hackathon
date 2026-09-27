# Implementation Plan

**Project:** Amazon Business Entity Resolution Pipeline  
**Methodology:** Spec-Driven & Test-Driven Development  
**Current Status:** ALL TASKS COMPLETED & VERIFIED

---

## Task Matrix & Status

| Task ID | Task Description | Dependencies | Files to Modify / Create | Status |
|---|---|---|---|---|
| **T01** | Data Layer & Strict Schema Validation | None | `src/utils.py`, `tests/test_data.py` | VERIFIED |
| **T02** | Text & Field Normalization (Names, Addresses, Open-set Countries) | T01 | `src/normalization.py`, `tests/test_normalization.py` | VERIFIED |
| **T03** | Official Macro F0.5 Metric & Singleton Scoring | None | `src/metrics.py`, `tests/test_metrics.py` | VERIFIED |
| **T04** | Scalable Multi-Rule Blocking & Candidate Generation | T01, T02 | `src/blocking.py`, `tests/test_blocking.py` | VERIFIED |
| **T05** | Pairwise Feature Extraction Engine | T02, T04 | `src/features.py`, `tests/test_features.py` | VERIFIED |
| **T06** | Supervised Pair Classifier & Threshold Calibration | T03, T05 | `src/model.py`, `tests/test_model.py` | VERIFIED |
| **T07** | End-to-End Inference Pipeline & Boundary Contracts | T04, T05, T06 | `src/pipeline.py`, `tests/test_pipeline.py` | VERIFIED |
| **T08** | Official Validator Execution & Output Verification | T07 | `output/*.tsv`, `student_resource/utils/validate_submission.py` | VERIFIED |
| **T09** | Documentation & Reproduction Guide | T08 | `code/business_entity_resolution/README.md`, `Documentation_template.md` | VERIFIED |

---

## Detailed Task Verification Summary

### T01: Data Layer & Strict Schema Validation (VERIFIED)
- Explicit tab separation (`sep="\t"`), `keep_default_na=False`, preserved exact string entity IDs.
- Validated column contracts (`entity_id`, `business_name`, `business_address`, `country`) and prefixes (`S1-`, `S2-`, `S3-`).
- 7/7 unit tests passing in `tests/test_data.py`.

### T02: Text & Field Normalization Engine (VERIFIED)
- Cleaned string formatting with NFKD unicode normalization, legal suffix extraction, address abbreviation expansions, and open-set country representation.
- Robust against France, US, India, and unknown country labels without hard-coded categorization.
- 7/7 unit tests passing in `tests/test_normalization.py`.

### T03: Official Macro F0.5 Metric (VERIFIED)
- Exact macro-averaged $F_{0.5}$ metric with full singleton credit (1.0 for true empty / predicted empty; 0.0 for false merge).
- Verified against official challenge worked example ($0.714$).
- 5/5 unit tests passing in `tests/test_metrics.py`.

### T04: Multi-Rule Blocking (VERIFIED)
- Multi-index inverted retrieval on exact normalized name, core distinctive tokens, character prefixes, and country/numeric address tokens.
- Validation blocking recall: **0.8754**, reduction ratio: **0.999617** ($>99.96\%$), average candidates/S1: **24.47**.
- 3/3 unit tests passing in `tests/test_blocking.py`.

### T05: Pairwise Feature Extraction (VERIFIED)
- 20-dimensional pairwise feature vector covering name similarities, address metrics, numeric overlaps, country match, missingness flags, and blocking rule provenance.
- 5/5 unit tests passing in `tests/test_features.py`.

### T06: Supervised Pair Matching Model (VERIFIED)
- `HistGradientBoostingClassifier` trained on positive and hard-negative pairs with balanced class weights.
- Decision threshold calibrated on validation split: optimal $\tau = 0.70$ achieving **0.9323 Macro F0.5**.
- 4/4 unit tests passing in `tests/test_model.py`.

### T07: End-to-End Pipeline & Candidate Boundary Invariant (VERIFIED)
- Batched streaming inference executed across all 1,732,544 Test Source 1 entities and 9.97M target records.
- Invariant strictly enforced: `output/candidate_pairs.tsv` snapshotted before model scoring; `matched_entity_ids ⊆ candidate_entity_ids`.
- Full integration test passing in `tests/test_pipeline.py`.

### T08: Official Validator Execution (VERIFIED)
- Executed `student_resource/utils/validate_submission.py` with `--check-ids` against full test set.
- Result: `PASS — no blocking issues found. Safe to submit.` (exit code 0).

### T09: Documentation & Reproduction Guide (VERIFIED)
- Completed `code/business_entity_resolution/README.md`, `code/business_entity_resolution/requirements.txt`, and `Documentation_template.md` with verified metrics and reproduction instructions.
