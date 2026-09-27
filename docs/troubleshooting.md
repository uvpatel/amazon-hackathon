# Troubleshooting & Operational Guide

This document catalogs common operational issues, runtime warnings, failure modes, and their direct engineering solutions.

---

## 1. High Memory Consumption or Out-Of-Memory (OOM)

### Symptom
Python process killed by OS kernel during inference on the full test set ($1.73\text{M}$ test records).

### Root Cause
Attempting to accumulate all candidate features or prediction dictionaries in a single in-memory list before writing.

### Remedy
- Ensure you run inference using `src.pipeline --mode predict`, which uses **streaming batch evaluation** ($B = 10,000$ entities per batch).
- In the streaming loop, candidate sets and prediction lines are flushed directly to disk using `open(mode="a")` append writes, keeping RAM consumption under $4\text{ GB}$.

---

## 2. Validator Failure: "Subset Invariant Violated"

### Symptom
`validate_submission.py` emits error: `Matched IDs not in candidate IDs for entity source1_xxxx`.

### Root Cause
Scoring or predicting on a candidate set that differs from the one written to `output/candidate_pairs.tsv` (e.g. secondary re-ranking or post-filtering).

### Remedy
- In `src/pipeline.py`, the candidate list retrieved from `BlockingIndex` is snapshotted to `candidate_pairs.tsv` *immediately before* scoring.
- Predicted matches are strictly filtered from that exact candidate set by thresholding $P(\text{match}) \ge \tau$.
- Never run post-processing steps that introduce novel IDs into `matching_results.tsv`.

---

## 3. Delimiter Errors: "Expected tab delimiter"

### Symptom
`load_tsv` raises `ValueError: Invalid TSV format` or `pandas.errors.ParserError`.

### Root Cause
Input file saved as comma-separated values (CSV) or containing raw tab characters within unquoted text fields.

### Remedy
- Ensure all source datasets are genuine TSV files with tab characters (`\t`) separating the 4 columns.
- The pipeline's `utils.load_tsv()` enforces `sep="\t"`, `quoting=csv.QUOTE_NONE`, and line-by-line validation to isolate malformed rows.

---

## 4. Portability / Library Issues on macOS (`libomp` Error)

### Symptom
`ImportError: dlopen(...): Library not loaded: /usr/local/opt/libomp/lib/libomp.dylib` when using LightGBM or XGBoost.

### Root Cause
LightGBM and XGBoost require OpenMP runtime libraries which are not pre-installed on macOS by default.

### Remedy
- Our champion pipeline deliberately uses **`sklearn.ensemble.HistGradientBoostingClassifier`**, which does not require external `libomp.dylib` or manual Homebrew installation.
- Verify your environment is using `src/model.py`, which imports directly from `sklearn.ensemble`.

---

## 5. Country Encoding / KeyErrors on Test Data (France)

### Symptom
`KeyError: 'France'` or categorical encoders throwing unrecognized category warnings on test data.

### Root Cause
Hardcoding categorical mappings or one-hot encoders to the training countries (`US`, `India`).

### Remedy
- The pipeline treats country strictly as an **open-set string** via `src/normalization.py::normalize_country`.
- Country agreement is evaluated via pairwise string equality $\mathbb{I}(\text{country}_1 == \text{country}_2)$, which handles any valid ISO code or novel country dynamically without fixed vocabulary dictionaries.
