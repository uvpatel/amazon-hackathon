# System Specification

## 1. Problem

For each Source 1 record, identify zero or more corresponding Source 2 and Source 3 records representing the same real-world business.

The task is asymmetric:

- Source 1 is the deduplicated reference.
- Source 2/3 are noisy lookup sources.
- One Source 1 entity can map to zero, one, or many records.

## 2. Pipeline

```text
TSV files
   |
   v
[Data Loader]
   |
   v
[Schema + ID Validation]
   |
   v
[Normalization]
   |
   +----------------------+
   |                      |
   v                      v
[Index Construction]   [Training Labels]
   |                      |
   v                      v
[Blocking / Candidate Generation]
   |
   v
[Pair Feature Extraction]
   |
   v
[Pair Scoring Model]
   |
   v
[Decision / Thresholding]
   |
   +--------------------+
   |                    |
   v                    v
candidate_pairs.tsv   matching_results.tsv
   |                    |
   +---------+----------+
             v
     [Submission Validator]
```

## 3. Architectural principles

### Deterministic preprocessing

The same input and configuration must produce the same normalized fields.

### Separation of concerns

- Loading must not perform matching.
- Normalization must not decide matches.
- Blocking must not become an implicit final classifier.
- Feature generation must be reusable for training and inference.
- Model scoring must not modify candidate membership.
- Output writing must not contain business logic.

### Auditability

For each final match, the system should be able to recover:

- Source 1 ID
- Source 2/3 ID
- blocking rule(s) that generated the pair
- normalized fields
- pair features
- model score
- final decision threshold

## 4. Proposed source tree

```text
src/business_entity_resolution/
├── __init__.py
├── config.py
├── cli.py
├── io/
│   ├── __init__.py
│   ├── loader.py
│   └── writer.py
├── schema/
│   ├── contracts.py
│   └── validation.py
├── normalization/
│   ├── text.py
│   ├── name.py
│   └── address.py
├── blocking/
│   ├── indexes.py
│   ├── rules.py
│   └── candidate_generator.py
├── features/
│   ├── lexical.py
│   ├── character.py
│   ├── token.py
│   └── pair_features.py
├── model/
│   ├── train.py
│   ├── predict.py
│   └── threshold.py
├── evaluation/
│   ├── labels.py
│   ├── metrics.py
│   └── validation_split.py
├── pipeline/
│   ├── train_pipeline.py
│   └── inference_pipeline.py
└── cli/
    └── main.py
```

## 5. Configuration

Do not scatter constants across modules. Centralize:

- input paths
- output paths
- normalization options
- blocking limits
- top-k values
- model parameters
- thresholds
- random seeds
- validation settings

Use a versioned configuration file so experiments are reproducible.
