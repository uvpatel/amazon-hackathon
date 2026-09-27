# Architecture & Technical Decisions

**Project:** Amazon Business Entity Resolution Pipeline  
**Date:** 2026-09-27

---

## Decision 1: Model Selection
- **Context:** `xgboost` and `lightgbm` installed on this host require `libomp.dylib`, which is absent from macOS by default and fails to load. The challenge constraints mandate: MIT/Apache 2.0 license, $\le 8$ billion parameters, and self-contained execution without reliance on broken native dynamic libraries.
- **Decision:** Use `HistGradientBoostingClassifier` and `LogisticRegression` from `scikit-learn` (v1.9.0).
- **Rationale:** `HistGradientBoostingClassifier` is an optimized tree-based gradient booster modeled directly on LightGBM. It is fast, handles missing values natively, has an Apache-compatible license (BSD 3-Clause), and executes natively on macOS arm64 without external OpenMP library issues.

---

## Decision 2: Self-Contained String & Similarity Metrics
- **Context:** The prototype had an unhandled import of `rapidfuzz`, which is not installed in the environment.
- **Decision:** Implement pure Python / `difflib` / `sklearn` similarity calculations for Levenshtein/gestalt token similarity, Jaccard token set similarity, character n-gram TF-IDF cosine similarity, and numeric prefix comparisons.
- **Rationale:** Prevents external binary package dependency issues, runs on any standard Python 3.8+ environment, and guarantees full reproducibility during submission audit.

---

## Decision 3: Multi-Rule Inverted Index Blocking with Adaptive Capping
- **Context:** Total records in train exceed 12.5M, and test has 1.7M S1 entities and ~10M S2/S3 entities. An all-pairs comparison ($1.7 \times 10^6 \times 10^7 \approx 1.7 \times 10^{13}$ pairs) is computationally impossible.
- **Decision:** Construct inverted indexes on:
  1. Normalized exact business name.
  2. High-entropy name tokens (filtered of ubiquitous legal stop-words).
  3. Character 3-gram prefixes.
  4. Extracted address numbers and postal tokens within matching country.
  Apply a configurable per-S1 candidate cap (e.g. top 10-25 candidates) with priority given to exact and high-overlap matches.
- **Rationale:** Prunes $>99.99\%$ of non-matching pairs while maintaining high candidate recall ceiling.

---

## Decision 4: Inference Candidate Snapshot Boundary
- **Context:** The challenge rules strictly require that `candidate_pairs.tsv` represents the exact candidates passed into the matching model, and every match in `matching_results.tsv` must exist in `candidate_pairs.tsv`.
- **Decision:** The pipeline generates and freezes candidates first, writes `candidate_pairs.tsv` directly from this frozen list, and then passes the identical candidate pairs to feature extraction and model scoring. No candidates are dropped after writing `candidate_pairs.tsv`.
- **Rationale:** Eliminates pipeline desynchronization and guarantees compliance with the official validator.

---

## Decision 5: Open-Set Country Representation
- **Context:** Training data contains `US` and `India`, whereas test data contains `France` in addition.
- **Decision:** Country is never one-hot encoded to a fixed two-country vocabulary. Instead, country agreement is modeled as:
  - Exact match boolean indicator (`country_s1 == country_s2_or_s3`).
  - Country missingness indicators.
- **Rationale:** Perfectly generalizes to `France` or any unseen country without throwing KeyError or dimensionality mismatch.
