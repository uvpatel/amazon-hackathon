# Configuration & CLI Reference

This document provides a comprehensive reference for all command-line arguments, environment settings, and tuning parameters used across the **Amazon Business Entity Resolution** pipeline.

---

## 1. CLI Entrypoint Overview

The main entry point is `src.pipeline`, executed with `PYTHONPATH=code/business_entity_resolution`:

```bash
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline [OPTIONS]
```

The pipeline supports two operational modes via the `--mode` flag:
1. `train`: Trains the gradient-boosted pairwise matcher, evaluates blocking recall, and calibrates the decision threshold on a validation split.
2. `predict`: Runs streaming batch inference over the test dataset, saving `output/matching_results.tsv` and `output/candidate_pairs.tsv`.

---

## 2. CLI Arguments Reference

| Flag | Mode | Type | Default Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--mode` | Both | `str` | `predict` | Operation mode: `train` or `predict`. |
| `--train-s1` | `train` | `str` | `student_resource/dataset/train/train_source1.tsv` | Path to Source 1 training TSV. |
| `--train-s2` | `train` | `str` | `student_resource/dataset/train/train_source2.tsv` | Path to Source 2 training TSV. |
| `--train-s3` | `train` | `str` | `student_resource/dataset/train/train_source3.tsv` | Path to Source 3 training TSV. |
| `--ground-truth` | `train` | `str` | `student_resource/dataset/train/train_ground_truth.tsv` | Path to ground truth training TSV. |
| `--test-s1` | `predict`| `str` | `student_resource/dataset/test/test_source1.tsv` | Path to Source 1 test TSV. |
| `--test-s2` | `predict`| `str` | `student_resource/dataset/test/test_source2.tsv` | Path to Source 2 test TSV. |
| `--test-s3` | `predict`| `str` | `student_resource/dataset/test/test_source3.tsv` | Path to Source 3 test TSV. |
| `--model-path` | Both | `str` | `output/model.pkl` | Path to save or load the serialized matching model. |
| `--output-dir` | `predict`| `str` | `output` | Directory where submission TSVs will be written. |
| `--threshold` | `predict`| `float`| `None` (uses calibrated threshold from model artifact, default `0.70`) | Match probability cutoff $\tau \in [0.0, 1.0]$. |

---

## 3. Algorithmic Hyperparameters

These parameters are defined in code constants across `src/blocking.py`, `src/features.py`, and `src/model.py`:

### Blocking & Indexing (`src/blocking.py`)
- `max_candidates_per_entity`: `50` (caps candidate list per Source 1 entity to control memory and feature extraction overhead).
- `min_token_len`: `3` (minimum character length for distinctive core name tokens).
- `prefix_len`: `4` (character length for n-gram prefix blocking).
- Stopwords / Business terms: Excluded from inverted index to avoid degenerate buckets (`inc`, `llc`, `ltd`, `corp`, `co`, `company`, `pvt`, `services`, `group`).

### Matching Model (`src/model.py`)
- `max_iter`: `200` (maximum gradient boosting iterations / trees).
- `max_leaf_nodes`: `31` (controls model complexity and prevents overfitting).
- `learning_rate`: `0.1` (shrinkage step size).
- `class_weight`: `'balanced'` (reweights positive instances to counteract the ~1:200 negative class imbalance).
- `random_state`: `42` (ensures exact deterministic reproducibility).

### Threshold Calibration Grid (`src/model.py`)
- Grid evaluation sweep: $\tau \in [0.20, 0.90]$ in steps of $0.05$.
- Objective metric: Macro $F_{0.5}$ (heavier weighting on precision to heavily penalize false merges).
- Calibrated optimal value: $\tau^* = 0.70$.

---

## 4. Directory Structure Defaults

By default, the pipeline expects input data under `student_resource/dataset/` and emits artifacts into `output/`:

```text
├── output/
│   ├── candidate_pairs.tsv
│   ├── matching_results.tsv
│   └── model.pkl
└── student_resource/
    └── dataset/
        ├── train/
        │   ├── train_source1.tsv
        │   ├── train_source2.tsv
        │   ├── train_source3.tsv
        │   └── train_ground_truth.tsv
        └── test/
            ├── test_source1.tsv
            ├── test_source2.tsv
            └── test_source3.tsv
```
