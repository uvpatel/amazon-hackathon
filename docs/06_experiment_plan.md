# Experiment Plan

## Phase 0 — Data audit

Measure:

- row counts by source
- missingness per field
- country frequencies without hard-coding countries
- duplicate normalized names
- duplicate normalized addresses
- average/median field lengths
- character/token distributions

Deliverable:

```text
reports/data_profile.md
```

## Phase 1 — Exact baseline

Blocking:

- normalized exact name
- exact address
- country-compatible fallback

Matching:

- deterministic exact evidence

Purpose:

Establish a lower bound and inspect obvious failure cases.

## Phase 2 — Fuzzy blocking

Add:

- character n-gram name retrieval
- address retrieval
- rare token indexes

Measure blocking recall and reduction ratio.

## Phase 3 — Feature model

Train a supervised pair classifier using:

- name similarities
- address similarities
- numeric overlap
- country
- missingness
- blocking evidence

Tune the decision threshold on validation.

## Phase 4 — Error analysis

Create buckets:

1. correct high-confidence match
2. false positive
3. false negative
4. singleton false positive
5. candidate-generation miss
6. ambiguous multi-match

For every error, identify whether the failure occurred in:

```text
normalization
blocking
features
model
threshold
```

This prevents wasting time tuning the model when the actual problem is candidate recall.

## Phase 5 — Candidate minimization

Once blocking recall is strong, reduce candidate volume.

Change one blocking parameter at a time:

- top-k name
- top-k address
- token rarity
- candidate cap

Record:

```text
blocking recall
candidate count
reduction ratio
macro F0.5
```

Never optimize candidate count alone.

## Phase 6 — Robustness

Explicitly test:

- unseen country labels
- empty fields
- transliteration
- abbreviations
- legal suffix changes
- word reordering
- typos
- partial addresses
- multiple true matches
- true singletons

## Experiment log

Each experiment should record:

```yaml
experiment_id:
git_commit:
config:
blocking:
features:
model:
threshold:
validation_f0_5:
precision:
recall:
blocking_recall:
avg_candidates:
p95_candidates:
notes:
```
