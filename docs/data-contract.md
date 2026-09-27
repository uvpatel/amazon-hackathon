# Data Contract & Invariant Specifications

This document defines the strict, non-negotiable data contracts, schema validations, and structural invariants enforced across all ingestion, transformation, and emission layers in the **Amazon Business Entity Resolution** system.

---

## 1. Physical TSV Storage Contract

1. **Delimiter**: All datasets must be encoded in UTF-8 text using explicit tab delimiters (`\t`).
2. **Escaping**: No surrounding quotes or field delimiters other than tab.
3. **Line Endings**: Standard Unix line feeds (`\n`) or CRLF (`\r\n`) handled gracefully by standard readers.
4. **Header Row**: The first line of every file must contain exact, case-sensitive column headers without leading or trailing whitespace.

---

## 2. Ingestion Contracts (`src/utils.py`)

When loading source datasets via `load_tsv(path, required_columns, id_prefix)`:

### Invariant Checks
1. **Schema Integrity**:
   - `entity_id`, `business_name`, `business_address`, `country` must all be present.
   - Any missing column triggers an immediate `ValueError`.
2. **Entity ID Prefix Enforcement**:
   - Every row's `entity_id` must begin with the expected source prefix (e.g. `source1_` for Source 1, `source2_` for Source 2, `source3_` for Source 3).
   - Any prefix mismatch triggers a `ValueError`.
3. **Uniqueness**:
   - Every `entity_id` within a source file must be unique. Duplicate keys trigger a `ValueError`.
4. **Missing Values**:
   - Null or missing text fields (`business_name`, `business_address`, `country`) are coerced to empty strings `""` to prevent `NoneType` attribute errors during normalization.

---

## 3. Ground Truth Contract (`parse_ground_truth`)

When parsing `train_ground_truth.tsv`:

1. **Header**: Exactly `source1_entity_id\tmatched_entity_ids`.
2. **Disallowed Self-Matches**:
   - `matched_entity_ids` must never reference a `source1_` entity ID.
   - Any self-reference triggers a validation failure.
3. **Empty String Convention**:
   - If a Source 1 entity has no matches in Source 2 or Source 3, `matched_entity_ids` is stored as an empty string `""` (representing a singleton).
4. **Multiple Matches**:
   - Multiple matching entities are comma-separated without spaces: e.g. `source2_0012,source3_0459`.

---

## 4. Submission Output Contracts

Both `output/candidate_pairs.tsv` and `output/matching_results.tsv` must strictly satisfy:

1. **Row Count Alignment**:
   - Exactly one row per test Source 1 entity.
   - The ordering and total count of `source1_entity_id` must match `test_source1.tsv` exactly ($1,732,544$ rows).
2. **Valid Target Domain**:
   - Any ID appearing in `candidate_entity_ids` or `matched_entity_ids` must belong to the valid test target pool (`test_source2.tsv` $\cup$ `test_source3.tsv`).
   - Cross-source corruption (e.g. `source1_` in match list) is strictly forbidden.
3. **Subset Invariant**:
   $$\text{matched\_entity\_ids} \subseteq \text{candidate\_entity\_ids}$$
   - Any predicted match that was not present in the candidate set triggers an immediate submission failure in the official validator.
4. **Idempotence**:
   - The candidate snapshot written to `candidate_pairs.tsv` represents the exact pool evaluated by the model, preventing candidate drift between blocking and scoring.
