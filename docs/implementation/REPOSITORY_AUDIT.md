# Repository Audit

**Date:** 2026-09-27  
**Project:** Amazon ML Challenge 2026 — Business Entity Resolution  
**Environment:** Python 3.14.6 on macOS (Darwin arm64)

---

## 1. Existing Architecture & Directory Structure

```text
/Users/urvilpatel/Hackathon/Amazon/
├── Documentation_template.md            # Official hackathon solution template
├── README.md                            # Root README
├── requirements.txt                     # Root requirements (empty)
├── .gitignore                           # Configured ignores (including student_resource/)
├── docs/                                # Specification documents
│   ├── 01_system_spec.md
│   ├── 02_data_contract.md
│   ├── 03_blocking_spec.md
│   ├── 04_matching_spec.md
│   ├── 05_validation_and_metrics.md
│   ├── 06_experiment_plan.md
│   ├── 07_implementation_plan.md
│   ├── 08_methodology.md
│   ├── 09_open_questions.md
│   ├── README.md
│   └── requirement.md                  # Hackathon problem statement & rules
├── student_resource/                    # Provided challenge resources (in .gitignore)
│   ├── Documentation_template.md       # Official template
│   ├── README.md                       # Official problem & submission guide
│   ├── dataset/
│   │   ├── train/
│   │   │   ├── train_source1.tsv       # 2,206,821 records (200MB)
│   │   │   ├── train_source2.tsv       # 5,034,616 records (467MB)
│   │   │   ├── train_source3.tsv       # 5,285,603 records (480MB)
│   │   │   └── train_ground_truth.tsv  # 2,206,821 records (121MB)
│   │   └── test/
│   │       ├── test_source1.tsv        # 1,732,544 records (167MB)
│   │       ├── test_source2.tsv        # 4,887,273 records (486MB)
│   │       └── test_source3.tsv        # 5,082,316 records (483MB)
│   └── utils/
│       └── validate_submission.py      # Official stdlib validator
├── output/
│   ├── matching_results.tsv            # Initial placeholder
│   └── candidate_pairs.tsv             # Initial placeholder
└── code/
    └── business_entity_resolution/
        ├── README.md                   # Reproduction documentation
        ├── requirements.txt            # Dependency list
        └── src/                        # Prototype source code
            ├── __init__.py
            ├── utils.py                # Initial text normalization & I/O
            ├── blocking.py             # Prototype blocking logic
            ├── matching.py             # Prototype matching (depends on rapidfuzz)
            └── pipeline.py             # Prototype pipeline entry point
```

---

## 2. Environment & Dependency Status

| Dependency | Status | Notes |
|---|---|---|
| Python | 3.14.6 | Standard CPython |
| `pandas` | 2.3.3 Installed | Tab-separated I/O supported |
| `numpy` | 2.5.0 Installed | Fast array and vector operations |
| `scikit-learn` | 1.9.0 Installed | Provides `HistGradientBoostingClassifier`, `LogisticRegression`, `TfidfVectorizer` |
| `scipy` | 1.18.0 Installed | Sparse matrices supported |
| `pytest` | 9.1.1 Installed | Unit testing framework |
| `difflib` | Standard Library | Fast sequence similarity matching |
| `xgboost` / `lightgbm` | Installed but broken | Missing `libomp.dylib` OpenMP runtime on macOS |
| `rapidfuzz` | NOT installed | Prototype `matching.py` has an unhandled import |

---

## 3. Working Components

- **Official Validator:** `student_resource/utils/validate_submission.py` works out of the box with zero external dependencies (Python stdlib).
- **Core ML libraries:** `sklearn`'s `HistGradientBoostingClassifier`, `LogisticRegression`, `TfidfVectorizer`, `numpy`, and `pandas` operate without errors.
- **Specifications:** Complete architectural contracts and rules documented in `docs/`.

---

## 4. Incomplete / Missing Components

1. **Prototype matching import:** `code/business_entity_resolution/src/matching.py` imports `rapidfuzz`, which is not installed. Needs to use self-contained, high-speed pure Python / `difflib` / `sklearn` string metrics.
2. **Data validation & contracts:** Prototype `utils.py` does not perform strict schema validation, ID prefix verification (`S1-`, `S2-`, `S3-`), or handle open-set country checking.
3. **High-scale blocking:** The prototype inverted index in `blocking.py` was an initial sketch that needs multi-rule blocking, token indexing, and candidate cap calibration to scale across millions of rows without memory exhaustion.
4. **Supervised matching model:** Prototype had a naive string similarity threshold rather than a trained supervised classifier on engineered pairwise features.
5. **Macro F0.5 evaluation:** Official metric computation (F0.5 with singleton handling) is not yet implemented in code.
6. **Inference candidate boundary:** Need to guarantee that `candidate_pairs.tsv` represents the exact candidates passed into the matching model, satisfying `matched_entity_ids ⊆ candidate_entity_ids`.
7. **Modular test suite:** No unit or integration tests under `tests/`.

---

## 5. Risks & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Large dataset volume (~2.2M train S1, 10M train S2+S3; 1.7M test S1, 10M test S2+S3) | OOM errors, hours of compute | Implement efficient sparse/inverted-index blocking with configurable candidate caps; validate on stratified train/val splits before full inference. |
| Country distribution shift (France in test, not train) | Pipeline crash or feature corruption | Implement open-set country handling without fixed categorical/one-hot encoding. |
| Singletons in evaluation | Severe F0.5 penalty if false merges occur on singletons | Model thresholding explicitly calibrated to protect singletons (F0.5 weights precision 2x). |
| Missing OpenMP (`libomp`) on macOS | `xgboost`/`lightgbm` failure | Use scikit-learn's `HistGradientBoostingClassifier` and `LogisticRegression`, which run flawlessly without external C runtime dependencies. |

---

## 6. Modification Plan

- **Files to Modify / Enhance:**
  - `code/business_entity_resolution/src/utils.py`
  - `code/business_entity_resolution/src/blocking.py`
  - `code/business_entity_resolution/src/matching.py`
  - `code/business_entity_resolution/src/pipeline.py`
  - `code/business_entity_resolution/requirements.txt`
  - `code/business_entity_resolution/README.md`
  - `Documentation_template.md`
- **New Files to Create:**
  - `code/business_entity_resolution/src/metrics.py` (official Macro F0.5 & singleton scoring)
  - `code/business_entity_resolution/src/features.py` (pairwise feature engineering)
  - `code/business_entity_resolution/src/model.py` (supervised classifier & threshold tuning)
  - `tests/` test suite (`test_data.py`, `test_normalization.py`, `test_blocking.py`, `test_features.py`, `test_metrics.py`, `test_pipeline.py`)
- **Files to Preserve Untouched:**
  - `student_resource/utils/validate_submission.py` (Official validator — MUST NOT BE MODIFIED)
  - `student_resource/dataset/` (Raw dataset files)
