# Automated Testing Guide & Test Inventory

This document details the automated test architecture, coverage structure, and test inventory implemented across `tests/`.

---

## 1. Testing Philosophy

The test suite enforces spec-driven reliability across five core testing layers:
1. **Contract & Schema Validation**: Verifying that invalid prefixes, missing columns, or bad delimiters fail immediately with informative errors.
2. **Deterministic Preprocessing**: Asserting that accents, legal suffixes, and country strings normalize identically.
3. **Blocking Correctness**: Guaranteeing that true candidates are retained and self-matches are impossible.
4. **Metric Integrity**: Confirming that singleton cases and the official challenge worked example compute exact scores.
5. **End-to-End Pipeline & Official Validator**: Running a full micro-pipeline integration test through `validate_submission.py`.

---

## 2. Running Tests

```bash
# Run the complete test suite
python3 -m pytest tests/ -v

# Run a specific test module
python3 -m pytest tests/test_metrics.py -v

# Run with execution timing
python3 -m pytest tests/ --durations=5
```

---

## 3. Comprehensive Test Inventory (32 Tests)

### A. Data & Contract Tests (`tests/test_data.py`)
- `test_load_tsv_valid`: Verifies correct parsing of valid TSV data.
- `test_load_tsv_missing_columns`: Verifies that missing required columns raise `ValueError`.
- `test_load_tsv_invalid_prefix`: Asserts failure when record ID does not match expected source prefix.
- `test_load_tsv_duplicate_id`: Verifies error on duplicate entity IDs within a source.
- `test_parse_ground_truth_valid`: Tests parsing of comma-separated ground truth pairs.
- `test_parse_ground_truth_reject_self_match`: Asserts error when `source1_` appears in match targets.
- `test_write_submission_file`: Tests TSV emission with exact tab delimiters and singleton rows.

### B. Normalization Tests (`tests/test_normalization.py`)
- `test_clean_base_text_accents`: Verifies NFKD diacritic removal (e.g. `Café` $\to$ `cafe`).
- `test_clean_base_text_ampersand_and_punctuation`: Tests expansion of `&` to `and` and punctuation removal.
- `test_normalize_name`: Tests legal suffix canonicalization (`Inc`, `LLC`, `Corp`).
- `test_get_core_name_tokens`: Asserts exclusion of business stop words and length thresholding.
- `test_normalize_address_abbreviations`: Tests expansion of `st`, `rd`, `ave`, `blvd`.
- `test_normalize_country_open_set`: Verifies open-set handling of `US`, `India`, `France`, etc.
- `test_extract_numeric_tokens`: Tests extraction of digit sequences from street addresses.

### C. Blocking Tests (`tests/test_blocking.py`)
- `test_exact_name_blocking`: Tests retrieval via exact normalized name index.
- `test_core_token_fuzzy_blocking`: Tests inverted index candidate retrieval across permuted tokens.
- `test_no_s1_self_matches_or_duplicates`: Guarantees no candidate matches $S_1$ to itself and results are deduplicated.

### D. Feature Engineering Tests (`tests/test_features.py`)
- `test_token_jaccard`: Verifies set overlap computation.
- `test_token_sort_similarity`: Tests order-invariant token sequence comparison.
- `test_extract_pair_features_exact`: Asserts feature values for identical entity pairs.
- `test_extract_pair_features_missing_fields_no_nan`: Ensures missing fields produce clean zeros/indicators without `NaN` values.
- `test_build_pair_feature_matrix`: Validates shape and float32 data type of feature matrix.

### E. Metrics Tests (`tests/test_metrics.py`)
- `test_official_worked_example`: Validates exact Macro $F_{0.5} = 0.4583$ on the official challenge example.
- `test_singleton_scoring`: Verifies $1.0$ for empty-true/empty-pred and $0.0$ for false merges.
- `test_perfect_match`: Asserts $1.0$ for identical true and predicted sets.
- `test_macro_f05`: Tests macro-averaging across diverse entity pairs.
- `test_blocking_metrics`: Validates candidate recall and reduction ratio formulas.

### F. Model & Inference Tests (`tests/test_model.py`)
- `test_fit_and_predict_proba`: Validates fitting and probability prediction on synthetic pairs.
- `test_predict_matches_subset_invariant`: Mathematically verifies that $\text{matched} \subseteq \text{candidates}$.
- `test_calibrate_threshold`: Tests threshold tuning grid for maximum Macro $F_{0.5}$.
- `test_save_and_load_model`: Tests serialization and round-trip deserialization via pickle.

### G. End-to-End Pipeline & Official Validator Test (`tests/test_pipeline.py`)
- `test_end_to_end_pipeline_and_official_validator`: Creates temporary synthetic Source 1, 2, 3 and Ground Truth files, executes full training and inference pipelines, runs `student_resource/utils/validate_submission.py`, and asserts zero validator errors (`PASS`).
