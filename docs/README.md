# Business Entity Resolution — Spec-Driven Implementation

## Status

This repository plan is derived from the supplied hackathon problem statement. The existing implementation repository and dataset are not included in the supplied attachment, so these documents define the target architecture and implementation contract rather than claiming an implementation has already been integrated.

## Objective

Build a reproducible entity-resolution pipeline that:

1. Reads Source 1/2/3 TSV files.
2. Learns matching behavior only from the supplied training data.
3. Generates a small, high-recall candidate set for every Source 1 entity.
4. Scores candidate pairs using learned/features-based matching.
5. Produces `matching_results.tsv`.
6. Produces the exact final inference candidate set as `candidate_pairs.tsv`.
7. Validates the outputs before submission.
8. Supports validation experiments using macro F0.5.

## Non-negotiable constraints

- TSV input/output with explicit tab separators.
- Every test Source 1 entity gets exactly one output row.
- Candidate IDs and match IDs may only reference Source 2/3 test records.
- Final matches must be a subset of final candidates.
- Empty lists represent singletons.
- No external entity lookup, geocoding, APIs, or internet data augmentation.
- Model must satisfy the challenge's MIT/Apache 2.0 and <=8B-parameter requirement.
- Country must be treated as an open-set string field; do not hard-code `{US, India}`.
- Candidate generation must materially reduce the search space.

## Target package

```text
submission/
├── output/
│   ├── matching_results.tsv
│   └── candidate_pairs.tsv
├── code/
│   └── business_entity_resolution/
│       ├── src/
│       ├── README.md
│       └── requirements.txt
└── Documentation_template.md
```

## Implementation order

See:
- `docs/01_system_spec.md`
- `docs/02_data_contract.md`
- `docs/03_blocking_spec.md`
- `docs/04_matching_spec.md`
- `docs/05_validation_and_metrics.md`
- `docs/06_experiment_plan.md`
- `docs/07_implementation_plan.md`
- `docs/08_methodology.md`
