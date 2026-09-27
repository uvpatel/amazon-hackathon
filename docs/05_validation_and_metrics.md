# Validation, Metrics, and Submission Checks

## Primary metric

The challenge uses macro-averaged F0.5 per Source 1 entity.

```text
F0.5 = (1.25 * Precision * Recall) /
       (0.25 * Precision + Recall)
```

Singletons are part of the macro average.

For a true singleton:

- predicted empty => score 1.0
- predicted any match => score 0.0

Therefore false positives on singleton entities are especially damaging.

## Entity-level scoring

For each Source 1 entity:

```text
TP = |predicted ∩ truth|
FP = |predicted - truth|
FN = |truth - predicted|
```

Then:

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
```

Handle the empty/empty case explicitly as a perfect score for that entity.

Then average the entity-level F0.5 scores.

## Validation split

Do not randomly split individual source rows independently.

The ground truth is grouped by Source 1. Validation must preserve complete Source 1 entities and their associated labels.

Recommended:

```text
training Source 1 entities -> fit model
validation Source 1 entities -> tune thresholds
```

For robust comparison, use multiple fixed seeds or folds.

## Critical validation metrics

Report:

| Metric | Why |
|---|---|
| Macro F0.5 | Primary objective |
| Precision | False merge control |
| Recall | Missed-match control |
| Singleton precision / false-positive rate | Critical for empty entities |
| Blocking recall | Candidate ceiling |
| Avg candidates/S1 | Scale |
| Median candidates/S1 | Typical cost |
| P95 candidates/S1 | Worst-case operational cost |
| Reduction ratio | Blocking efficiency |
| Prediction coverage | Whether all S1 rows are emitted |

## Threshold sweep

For each threshold:

1. Score validation candidates.
2. Convert scores to match lists.
3. Compute macro F0.5.
4. Record precision/recall.
5. Record singleton false-positive rate.
6. Select the threshold based on validation F0.5, while inspecting precision and blocking recall.

Do not tune against the public leaderboard repeatedly as a substitute for local validation.

## Submission validator

Always run:

```bash
python3 utils/validate_submission.py   --matching output/matching_results.tsv   --candidate output/candidate_pairs.tsv   --test-dir dataset/test
```

Treat validator failure as a hard build failure.

## Additional invariants

Programmatically assert:

```text
set(output.S1) == set(test_source1.S1)

matched_ids ⊆ candidate_ids

matched_ids ⊆ (test_source2.ids ∪ test_source3.ids)

candidate_ids ∩ test_source1.ids == ∅

no duplicate S1 output rows

no duplicate IDs inside lists
```
