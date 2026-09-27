# Business Entity Resolution Pipeline

This repository contains the end-to-end code for resolving and matching business entity records across independent, noisy data sources.

---

## 1. Directory Structure

```text
code/business_entity_resolution/
├── README.md               # End-to-end reproduction guide
├── requirements.txt        # Pinned dependencies & environment
└── src/                    # Source code modules
    ├── __init__.py
    ├── utils.py            # Data loading, text normalization, and I/O
    ├── blocking.py         # Candidate generation / blocking index
    ├── matching.py         # Similarity scoring & classification
    └── pipeline.py         # End-to-end reproduction entry point
```

---

## 2. Environment Setup

### Prerequisites
- Python 3.9+
- `pip` or `conda`

### Installation
From the `code/business_entity_resolution` directory, install the required packages:

```bash
pip install -r requirements.txt
```

---

## 3. End-to-End Reproduction Workflow

The pipeline executes the four core stages in sequence: **Data Ingestion → Blocking → Matching → Output Generation**.

```
[Raw Sources] ──> [1. Data Preprocessing] ──> [2. Candidate Blocking] ──> [3. Scoring & Matching] ──> [4. Output TSVs]
```

### Running the Pipeline
Execute the pipeline module from the project root or the code directory:

```bash
# Run from repository root:
python -m code.business_entity_resolution.src.pipeline \
  --data_dir ./data \
  --output_dir ./output \
  --threshold 0.80
```

### Command-line Arguments
- `--data_dir`: Path to the directory containing input datasets (`source_1.tsv`, `source_2.tsv`, `source_3.tsv`). Default: `./data`.
- `--output_dir`: Path to the output directory where resulting TSV files will be saved. Default: `../../output`.
- `--threshold`: Similarity threshold cutoff for accepting an entity match (range: 0.0 - 1.0). Default: `0.80`.

---

## 4. Pipeline Stages

1. **Data Preprocessing & Normalization (`src/utils.py`)**:
   - Cleans string noise, unifies unicode characters, and standardizes business names, address terms, and punctuation.
2. **Candidate Generation / Blocking (`src/blocking.py`)**:
   - Generates n-gram and prefix blocking keys to efficiently prune the pair search space while maintaining high recall.
   - Generates `output/candidate_pairs.tsv`.
3. **Similarity Scoring & Matching (`src/matching.py`)**:
   - Computes weighted token similarity metrics across matched candidate pairs.
   - Selects top candidate predictions meeting the calibrated decision threshold.
4. **Output Generation (`src/pipeline.py`)**:
   - Writes `output/matching_results.tsv` (for leaderboard evaluation) and `output/candidate_pairs.tsv` (for blocking audit).
