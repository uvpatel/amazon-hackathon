# Acceptance Criteria Checklist

**Project:** Amazon Business Entity Resolution Pipeline  
**Updated:** 2026-09-27  
**Status:** All 26 Criteria VERIFIED

---

| Status | ID | Criterion | Evidence / Verification Method |
|---|---|---|---|
| [x] | AC-01 | Existing repository inspected and preserved | Non-destructive reconnaissance; all user and existing files preserved |
| [x] | AC-02 | Repository audit created (`docs/implementation/REPOSITORY_AUDIT.md`) | Verified present with architecture and risk analysis |
| [x] | AC-03 | Specifications and implementation plan created | Verified present in `docs/implementation/IMPLEMENTATION_PLAN.md` |
| [x] | AC-04 | Input schemas validated with strict column types | `pytest tests/test_data.py` passed (7/7 tests) |
| [x] | AC-05 | TSV parsing uses explicit tab separators (`sep="\t"`, `keep_default_na=False`) | Implemented in `src/utils.py` and validated by unit tests |
| [x] | AC-06 | Entity IDs preserved as exact strings with prefixes | `test_data.py` passes; leading zeros and string types preserved |
| [x] | AC-07 | Open-set country support verified (France, US, India, unknown) | `test_normalize_country_open_set` passes; verified on France in test data |
| [x] | AC-08 | Normalization has comprehensive unit tests | `pytest tests/test_normalization.py` passed (7/7 tests) |
| [x] | AC-09 | Candidate generation avoids exhaustive all-pairs inference | Inverted index blocking prunes $>99.96\%$ of search space |
| [x] | AC-10 | Blocking recall measured on validation | Validation blocking recall: **0.8754** on held-out split |
| [x] | AC-11 | Candidate count and reduction ratio measured | Avg 24.47 candidates/S1; reduction ratio: **0.999617** |
| [x] | AC-12 | Candidate file represents the exact pairs scored by the model | Invariant strictly enforced at inference boundary and tested |
| [x] | AC-13 | Matching supports zero, one, or multiple matches | Multi-match threshold logic verified in `tests/test_model.py` |
| [x] | AC-14 | Official macro F0.5 implemented and tested | `test_official_worked_example` matches problem statement (0.714) |
| [x] | AC-15 | Singleton scoring implemented correctly (empty/empty=1.0, empty/pred=0.0) | `test_singleton_scoring` passed; 460,915 test singletons preserved |
| [x] | AC-16 | Threshold selected using validation only | Calibrated threshold $\tau = 0.70$ on validation set (F0.5: 0.9323) |
| [x] | AC-17 | Both required TSV files generated (`matching_results.tsv`, `candidate_pairs.tsv`) | Both generated in `output/` directory |
| [x] | AC-18 | Every test Source 1 entity has exactly one row in both files | Exactly 1,732,544 rows in both files (matches `test_source1.tsv`) |
| [x] | AC-19 | Every predicted match is in the candidate set (`matched_ids ⊆ candidate_ids`) | Verified by `validate_submission.py`; zero violations |
| [x] | AC-20 | Every candidate and match references an existing test S2/S3 ID | Verified by `validate_submission.py --check-ids` against 9,969,589 target IDs |
| [x] | AC-21 | No duplicate IDs in output lists | Verified by official validator; zero duplicates |
| [x] | AC-22 | Official validator passes (`python3 utils/validate_submission.py`) | Exit code 0: `PASS — no blocking issues found. Safe to submit.` |
| [x] | AC-23 | Training and inference instructions documented | Verified in `code/business_entity_resolution/README.md` |
| [x] | AC-24 | Dependency versions documented and compatible | Pinned in `code/business_entity_resolution/requirements.txt` |
| [x] | AC-25 | Methodology document reflects actual implementation | Fully completed in `Documentation_template.md` |
| [x] | AC-26 | No external entity lookup or web API used | 100% self-contained local ML pipeline |
