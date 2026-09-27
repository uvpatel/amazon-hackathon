# Amazon Business Entity Resolution — Production Pipeline

This repository contains the end-to-end, spec-driven machine learning pipeline for resolving and matching business entity records across three independent, noisy data sources without common identifiers.

---

## 1. Directory Structure

```text
code/business_entity_resolution/
├── README.md               # End-to-end reproduction guide
├── requirements.txt        # Verified, pinned dependencies
└── src/                    # Modular source code
    ├── __init__.py
    ├── utils.py            # Strict TSV I/O, schema validation, contract enforcement
    ├── normalization.py    # Deterministic name, address, and open-set country normalization
    ├── metrics.py          # Official Macro-averaged F0.5 metric & singleton scoring
    ├── blocking.py         # Multi-rule inverted index candidate generator
    ├── features.py         # Vectorized pairwise feature extraction
    ├── model.py            # HistGradientBoosting classifier & threshold calibration
    └── pipeline.py         # End-to-end training, validation & streaming inference CLI
```

---

## 2. Environment Setup

### Prerequisites
- Python 3.9+ (tested on Python 3.14.6)
- Standard packages: `pandas`, `numpy`, `scikit-learn`, `scipy`, `pytest`

### Installation
From the repository root or `code/business_entity_resolution/` directory:

```bash
pip install -r code/business_entity_resolution/requirements.txt
```

---

## 3. Architecture & Core Workflow

The solution operates through a multi-stage entity-resolution architecture:

```text
[Source 1/2/3 TSV Files]
       │
       ▼
[Data Layer & Contract Validation] (Explicit TSV tab delimiter, ID prefix checks)
       │
       ▼
[Normalization Engine] (Deterministic cleaning, NFKD unicode, address abbreviations, open-set country)
       │
       ▼
[Candidate Generation / Blocking] (Exact name, core tokens, character prefixes, numeric tokens)
       │
       ▼
[Candidate Boundary Snapshot] ───► output/candidate_pairs.tsv (EXACT model input set)
       │
       ▼
[Pairwise Feature Extraction] (20 pairwise lexical, token, numeric, country & missingness features)
       │
       ▼
[Supervised Pair Scoring] (HistGradientBoostingClassifier with balanced class weighting)
       │
       ▼
[Validation Thresholding] (Calibrated against Macro F0.5 on held-out S1 validation split)
       │
       ▼
[Match Assignment] ───────────────► output/matching_results.tsv (Guaranteed subset of candidate set)
```

---

## 4. End-to-End Execution Commands

### Run Complete Test Suite
```bash
python3 -m pytest tests/ -v
```

### 1. Training & Validation
Train the `HistGradientBoostingClassifier`, calibrate the decision threshold on validation entities, and measure blocking metrics:

```bash
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline \
  --mode train \
  --train-s1 student_resource/dataset/train/train_source1.tsv \
  --train-s2 student_resource/dataset/train/train_source2.tsv \
  --train-s3 student_resource/dataset/train/train_source3.tsv \
  --ground-truth student_resource/dataset/train/train_ground_truth.tsv \
  --model-path output/model.pkl
```

### 2. Test Inference & Output Generation
Generate `output/matching_results.tsv` and `output/candidate_pairs.tsv` from the test dataset:

```bash
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline \
  --mode predict \
  --test-s1 student_resource/dataset/test/test_source1.tsv \
  --test-s2 student_resource/dataset/test/test_source2.tsv \
  --test-s3 student_resource/dataset/test/test_source3.tsv \
  --model-path output/model.pkl \
  --output-dir output
```

### 3. Run Official Submission Validator
```bash
python3 student_resource/utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir student_resource/dataset/test
```

---

## 5. Measured Performance & Results

- **Validation Macro F0.5:** `0.9323` (at optimal threshold `0.70`)
- **Validation Blocking Recall:** `0.8754`
- **Validation Reduction Ratio:** `0.999617` (99.96% search space pruned)
- **Average Candidates per S1:** `24.47`
- **Official Submission Validator Status:** `PASS`
