# Methodology Document Draft

## 1. Overview

The solution uses a multi-stage entity-resolution pipeline separating candidate generation from supervised pair classification.

Source 1 is treated as the reference entity set. Source 2 and Source 3 are candidate match sources.

The pipeline consists of:

1. deterministic normalization
2. multi-rule blocking
3. pair-level feature engineering
4. supervised classification
5. validation-driven thresholding
6. submission validation

## 2. Data Processing

All challenge files are read as TSV using an explicit tab separator.

Raw fields are preserved. Additional normalized representations are generated for names and addresses.

Normalization is designed to reduce formatting variation without relying on external business databases.

## 3. Candidate Generation

Candidate generation uses multiple complementary retrieval rules.

Name-based rules capture exact normalized names, character-level similarity, and informative token overlap.

Address-based rules capture token overlap, numeric identifiers, and character similarity.

Country is used as an observed feature/blocking signal without assuming a fixed set of countries.

The union of these rules is deduplicated and subjected to final candidate controls before model inference.

`candidate_pairs.tsv` is generated at this final inference boundary.

## 4. Feature Engineering

Candidate pairs receive features describing:

- name similarity
- address similarity
- numeric-token agreement
- country agreement
- field missingness
- evidence from blocking rules

The model receives only information available in the supplied challenge data.

## 5. Matching Model

A supervised binary pair classifier estimates the probability that a candidate pair represents the same business.

The system does not impose a one-to-one constraint because a Source 1 entity may have multiple matches.

A validation-selected threshold converts model probabilities into final match decisions.

## 6. Evaluation

The primary local metric is macro F0.5 at the Source 1 entity level.

Validation also measures blocking recall, precision, recall, singleton false-positive behavior, average candidate count, and reduction ratio.

## 7. Reproducibility

The final package contains:

- source code
- pinned dependencies
- configuration
- output files
- methodology documentation

The complete pipeline can regenerate the submission from the supplied training and test data.

## 8. Fair Play

No external databases, entity-resolution services, geocoding APIs, internet lookups, or external business data augmentation are used.
