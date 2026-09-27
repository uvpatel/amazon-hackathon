# Data Contract

## Input files

### Training

```text
dataset/train/train_source1.tsv
dataset/train/train_source2.tsv
dataset/train/train_source3.tsv
dataset/train/train_ground_truth.tsv
```

### Test

```text
dataset/test/test_source1.tsv
dataset/test/test_source2.tsv
dataset/test/test_source3.tsv
```

## Entity schema

Each source file:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `entity_id` | string | yes | Unique source-prefixed identifier |
| `business_name` | string | yes/nullable | Noisy business name |
| `business_address` | string | yes/nullable | Noisy address |
| `country` | string | yes/nullable | Open-set country label |

The source is derived from the file and/or ID prefix. Do not introduce a hard-coded country vocabulary.

## Ground truth

```text
source1_entity_id    matched_entity_ids
```

`matched_entity_ids` is a comma-separated list and may be empty.

## Output contract

### matching_results.tsv

Exactly:

```text
source1_entity_id    matched_entity_ids
```

Requirements:

- exactly one row for every test Source 1 entity
- no duplicate Source 1 IDs
- no S1 IDs in the match list
- all referenced IDs must exist in test Source 2/3
- no duplicate IDs within a list
- empty list for singleton predictions

### candidate_pairs.tsv

Exactly:

```text
source1_entity_id    candidate_entity_ids
```

The candidates must be the **final set actually passed into the matching model**.

Every predicted match must exist in this candidate set.

## TSV handling

Always use:

```python
pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
```

Never rely on comma-separated parsing.

## Loader checks

Fail fast on:

- missing required columns
- duplicate entity IDs
- malformed IDs
- unexpected source prefixes
- unreadable TSVs
- inconsistent ID types
