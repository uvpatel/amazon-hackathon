# Implementation Plan

## Milestone 1 — Repository bootstrap

Create:

```text
code/business_entity_resolution/
├── src/business_entity_resolution/
├── README.md
└── requirements.txt
```

Add:

- package entry point
- configuration object
- logging
- deterministic random seed

## Milestone 2 — Data layer

Implement:

- TSV loader
- schema validation
- ID/source validation
- ground-truth parser
- output writer

Acceptance criteria:

- all supplied files load correctly
- malformed schemas fail clearly
- no comma/TSV ambiguity

## Milestone 3 — Normalization

Implement independent deterministic functions:

```text
normalize_name()
normalize_address()
normalize_country()
tokenize()
extract_numeric_tokens()
```

Keep raw values unchanged.

Acceptance criteria:

- unit tests for punctuation
- casing
- whitespace
- legal suffixes
- `&`/`and`
- numbers
- missing values

## Milestone 4 — Blocking

Implement:

```text
build_indexes()
generate_candidates()
finalize_candidates()
```

Every candidate should carry provenance:

```text
candidate_id
blocking_rules
```

Acceptance criteria:

- no S1 candidates
- no unknown IDs
- no duplicate pairs
- validation blocking recall measured
- candidate count substantially below all-pairs

## Milestone 5 — Feature extraction

Implement a vectorized/batched pair-feature pipeline.

Avoid Python nested loops over all possible source pairs.

Acceptance criteria:

- feature schema versioned
- no NaNs reaching model unexpectedly
- deterministic output

## Milestone 6 — Model

Implement:

```text
fit()
predict_proba()
```

and threshold selection.

Acceptance criteria:

- validation F0.5 computed
- threshold reproducible
- model artifact/config reproducible

## Milestone 7 — End-to-end inference

Implement:

```text
load -> normalize -> index -> block -> feature -> score -> threshold -> write
```

Acceptance criteria:

- every test S1 has a row
- every match exists in candidate file
- singleton rows are retained

## Milestone 8 — Submission packaging

Build:

```text
<team>_submission.zip
```

and run the official validator.

## Definition of done

The implementation is complete only when:

- training/validation runs from a clean environment
- test inference runs from a clean environment
- both required TSVs are generated
- validator returns PASS
- candidate set is the exact model input
- methodology is documented
- no external lookup occurs
- requirements are pinned
