# Reproducibility Guide

This document provides exact, deterministic instructions for reproducing the entire experimental and submission pipeline of the **Amazon Business Entity Resolution** system from scratch.

---

## 1. Principles of Determinism

To guarantee identical results across runs, machines, and operating systems, the pipeline enforces:
1. **Fixed Random Seeds**: All stochastic processes (data splitting, class-balanced sampling, tree building) use `random_state=42`.
2. **Deterministic String Normalization**: Normalization uses Unicode Standard NFKD decomposition followed by regex patterns compiled without locale dependence.
3. **Deterministic Token Sorting**: Token sets are converted to sorted Python lists before computing string metrics.
4. **Frozen Dependencies**: Pinned package versions are specified in `requirements.txt`.
5. **No External Network Calls**: Zero calls to remote geocoding, translation, or entity matching APIs.

---

## 2. Step-by-Step Reproduction Instructions

### Step 1: Environment Isolation

```bash
# Clone the repository
git clone https://github.com/uvpatel/amazon-hackathon.git
cd amazon-hackathon

# Initialize clean virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install verified dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Verification of Unit Tests

Run the test suite to verify deterministic behavior across all 32 tests:

```bash
python3 -m pytest tests/ -v
```

All 32 tests must pass with exit code `0`.

### Step 3: Reproduce Model Training & Threshold Tuning

Train the model and save the artifact to `output/model.pkl`:

```bash
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline \
  --mode train \
  --train-s1 student_resource/dataset/train/train_source1.tsv \
  --train-s2 student_resource/dataset/train/train_source2.tsv \
  --train-s3 student_resource/dataset/train/train_source3.tsv \
  --ground-truth student_resource/dataset/train/train_ground_truth.tsv \
  --model-path output/model.pkl
```

**Deterministic Outputs:**
- Model weights and calibrated threshold ($\tau = 0.70$) serialized to `output/model.pkl`.
- Validation Macro $F_{0.5}$ metric: `0.9323`.

### Step 4: Reproduce Test Inference

Generate the submission artifacts:

```bash
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline \
  --mode predict \
  --test-s1 student_resource/dataset/test/test_source1.tsv \
  --test-s2 student_resource/dataset/test/test_source2.tsv \
  --test-s3 student_resource/dataset/test/test_source3.tsv \
  --model-path output/model.pkl \
  --output-dir output
```

**Deterministic Outputs:**
- `output/candidate_pairs.tsv` ($1,732,544$ rows)
- `output/matching_results.tsv` ($1,732,544$ rows)

### Step 5: Official Validation Verification

Run the official validation script:

```bash
python3 student_resource/utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir student_resource/dataset/test
```

**Expected Result:**
```text
Summary:
Total issues: 0 (0 blocking, 0 warnings)
Status: PASS — no blocking issues found. Safe to submit.
```
