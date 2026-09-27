# Matching Model Specification

## Objective

Classify each final candidate pair as:

```text
MATCH / NON_MATCH
```

while preserving the possibility that one Source 1 entity has multiple true matches.

Do not force one-to-one assignment.

## Recommended baseline

Start with a lightweight supervised pair classifier such as logistic regression or a tree-based classifier over engineered pair features.

This is preferable as the first implementation because:

- it is fast
- interpretable
- easy to validate
- compatible with the <=8B requirement
- easy to audit
- avoids unnecessary model complexity

A stronger model can be added only after a strong baseline exists.

## Pair features

### Name features

- normalized exact equality
- normalized token Jaccard
- character n-gram cosine similarity
- edit similarity
- token-sort similarity
- token overlap count
- length ratio
- rare-token overlap

### Address features

- normalized exact equality
- token Jaccard
- character n-gram cosine
- edit similarity
- numeric-token overlap
- postal/PIN-like token equality where present
- house-number equality where present
- address length ratio

### Cross-field features

- country exact match
- missingness indicators
- name/address evidence interaction
- number of independent blocking rules that generated the candidate

The last feature is useful as a model feature only if it is derived without label leakage.

## Normalization requirements

Normalization should produce multiple views rather than destroying information.

For each field maintain:

```text
raw
normalized
tokenized
character representation
numeric tokens
```

Do not aggressively remove information from the only representation.

## Decision strategy

Because evaluation is F0.5 and false merges are costly, threshold selection must be validation-driven.

Evaluate:

```text
threshold -> macro F0.5
threshold -> precision
threshold -> recall
threshold -> singleton false-positive rate
```

Do not optimize accuracy.

## Multiple matches

For each Source 1 entity:

```text
score every final candidate
keep candidates >= threshold
```

Do not select only the highest-scoring candidate.

## Optional confidence tiers

For debugging, classify predictions into:

- high-confidence
- medium-confidence
- rejected

Only the configured acceptance threshold determines the actual submission.

## Model reproducibility

Record:

- model class
- package version
- feature configuration
- random seed
- training partition
- threshold
- configuration version
