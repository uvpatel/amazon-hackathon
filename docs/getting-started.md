# Getting Started

This guide provides a rapid, step-by-step walkthrough to get the **Amazon Business Entity Resolution** pipeline up and running in under five minutes.

---

## Prerequisites

- **Operating System**: macOS, Linux, or Windows (WSL recommended).
- **Python**: 3.9 or higher (tested up to 3.14.6).
- **System Memory**: 8 GB minimum (16 GB recommended for full dataset inference).

---

## Step 1: Clone Repository & Create Environment

```bash
# 1. Clone the repository
git clone https://github.com/uvpatel/amazon-hackathon.git
cd amazon-hackathon

# 2. Create an isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 2: Verify Installation with Test Suite

Before executing training or inference, run the automated test suite to ensure that string normalization, inverted indexing, pairwise feature extraction, and metric calculation function correctly on your machine:

```bash
python3 -m pytest tests/ -v
```

**Expected output:**
```text
============================== 32 passed in 1.23s ==============================
```

---

## Step 3: Train Model & Calibrate Threshold

Train the `HistGradientBoostingClassifier` on the training dataset. The script builds a candidate blocking pool, extracts 20 pairwise features, trains the boosting model with balanced class weights, and evaluates Macro $F_{0.5}$ across threshold values $\tau \in [0.20, 0.90]$ on a held-out validation split:

```bash
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline \
  --mode train \
  --train-s1 student_resource/dataset/train/train_source1.tsv \
  --train-s2 student_resource/dataset/train/train_source2.tsv \
  --train-s3 student_resource/dataset/train/train_source3.tsv \
  --ground-truth student_resource/dataset/train/train_ground_truth.tsv \
  --model-path output/model.pkl
```

The resulting model is saved to `output/model.pkl`.

---

## Step 4: Run Inference to Generate Submission Artifacts

Execute streaming batch prediction over the test dataset to generate the two required submission files:
1. `output/candidate_pairs.tsv`: The exact candidate set considered for each test Source 1 entity.
2. `output/matching_results.tsv`: The final predicted matches ($\text{matches} \subseteq \text{candidates}$).

```bash
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline \
  --mode predict \
  --test-s1 student_resource/dataset/test/test_source1.tsv \
  --test-s2 student_resource/dataset/test/test_source2.tsv \
  --test-s3 student_resource/dataset/test/test_source3.tsv \
  --model-path output/model.pkl \
  --output-dir output
```

---

## Step 5: Run the Official Submission Validator

Verify that the generated submission files comply with all challenge rules and invariants:

```bash
python3 student_resource/utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir student_resource/dataset/test
```

**Expected output:**
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

## Next Steps

- For an in-depth understanding of the system design, read [Project Architecture](project-architecture.md).
- To examine blocking and indexing mechanics, see [Candidate Generation](candidate-generation.md).
- To inspect feature representations and model hyperparameters, see [Matching Model](matching-model.md).
