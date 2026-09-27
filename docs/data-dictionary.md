# Data Dictionary & Field Reference

This document provides a field-by-field reference for all datasets used in the **Amazon Business Entity Resolution** system, including schema specifications, nullability rules, noise characteristics, and examples.

---

## 1. Source Datasets (`source1`, `source2`, `source3`)

All input source files share the same 4-column schema in TSV format:

| Column Name | Data Type | Nullable? | ID Prefix | Description & Noise Profile |
| :--- | :--- | :--- | :--- | :--- |
| `entity_id` | `string` | **No** | `source1_` / `source2_` / `source3_` | Unique record identifier within the source dataset. Strict alphanumeric string prefixed by source name. |
| `business_name` | `string` | Yes | N/A | Commercial or legal business name. May contain abbreviations, DBAs, suffixes (`Inc`, `LLC`, `Pvt Ltd`), punctuation, and transliterations. |
| `business_address` | `string` | Yes | N/A | Physical address string. May be missing, truncated, landmark-based ("Near Metro Station"), or permuted. |
| `country` | `string` | Yes | N/A | Open-set country string (e.g. `US`, `India`, `France`). May have inconsistent casing or whitespace. |

### Source-Specific Characteristics

#### Source 1 (Reference Entities)
- **Role**: Reference clean catalog.
- **Completeness**: High. Almost all records contain business name, address, and country.
- **Duplicates**: Fully deduplicated internally (no duplicate entities within Source 1).
- **ID Example**: `source1_000142`

#### Source 2 (Registry Source A)
- **Role**: Noisy commercial partner records.
- **Completeness**: High name completeness; **sparse address data**. Many addresses are empty or limited to city names.
- **Noise Profile**: Business names frequently match legal entities closely, but lack address disambiguation.
- **ID Example**: `source2_005912`

#### Source 3 (Registry Source B)
- **Role**: Secondary commercial registry.
- **Completeness**: Low name completeness; **detailed address data**.
- **Noise Profile**: Frequent use of colloquial trade names, store numbers, or DBAs (e.g., "McDonald's Store #4021" vs "McDonald's Corporation"), coupled with detailed street-level addresses.
- **ID Example**: `source3_018234`

---

## 2. Ground Truth Dataset (`train_ground_truth.tsv`)

The training supervision dataset mapping Source 1 entities to matching records in Source 2 and Source 3:

| Column Name | Data Type | Nullable? | Description |
| :--- | :--- | :--- | :--- |
| `source1_entity_id` | `string` | **No** | Identifier corresponding to an entity in `train_source1.tsv`. |
| `matched_entity_ids` | `string` | Yes (empty string) | Comma-separated list of matching entity IDs from Source 2 and Source 3. Empty string if singleton. |

### Ground Truth Invariants
1. `source1_entity_id` must begin with `source1_`.
2. Every ID inside `matched_entity_ids` must begin with `source2_` or `source3_`.
3. Self-matches (`source1_` inside `matched_entity_ids`) are illegal.
4. If a Source 1 entity has no matches in Source 2 or Source 3, `matched_entity_ids` is empty (`""`).

---

## 3. Submission Output Datasets

### A. Candidate Pairs (`output/candidate_pairs.tsv`)

The blocking candidate set considered by the model for scoring:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `source1_entity_id` | `string` | Test Source 1 identifier. Every test S1 entity has exactly one row. |
| `candidate_entity_ids` | `string` | Comma-separated list of candidate IDs retrieved during blocking from test Source 2 and Source 3. |

### B. Matching Results (`output/matching_results.tsv`)

The final predicted matches uploaded to the leaderboard:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `source1_entity_id` | `string` | Test Source 1 identifier. Every test S1 entity has exactly one row. |
| `matched_entity_ids` | `string` | Comma-separated list of predicted matching IDs where $P(\text{match}) \ge \tau$. Empty if singleton. |

### Subset Guarantee
$$\forall e \in \text{Test Source 1}: \quad \text{matched\_entity\_ids}(e) \subseteq \text{candidate\_entity\_ids}(e)$$
