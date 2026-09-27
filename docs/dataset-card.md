# Dataset Card: Amazon Business Entity Resolution Dataset

Following standard Dataset Card conventions (Gebru et al., 2018), this document provides a comprehensive overview of the training and test datasets provided for the **Amazon ML Challenge 2026**.

---

## 1. Dataset Overview & Motivation

The dataset was curated by the Amazon ML Challenge 2026 committee to benchmark scalable entity resolution algorithms on realistic industrial business data without common cross-system keys.

### Dataset Partitions:
- **Training Set**:
  - `train_source1.tsv`: Reference businesses ($100,000+$ records)
  - `train_source2.tsv`: Commercial registry records ($2,500,000+$ records)
  - `train_source3.tsv`: Secondary commercial registry records ($2,500,000+$ records)
  - `train_ground_truth.tsv`: Ground truth match labels for Source 1 entities
- **Test Set**:
  - `test_source1.tsv`: Reference businesses ($1,732,544$ records)
  - `test_source2.tsv`: Commercial registry records ($5,000,000$ records)
  - `test_source3.tsv`: Secondary commercial registry records ($5,000,000$ records)
  - No ground truth labels provided (blind leaderboard evaluation)

---

## 2. Data Fields & Types

All source files share the 4-column schema:

```text
entity_id            string (e.g. "source1_0001", "source2_0002", "source3_0003")
business_name        string (legal or trade name, nullable)
business_address     string (street, city, state, postal, nullable)
country              string (open-set country name/code, nullable)
```

Ground truth schema:
```text
source1_entity_id    string (e.g. "source1_0001")
matched_entity_ids   string (comma-separated list of matching source2 and source3 IDs; empty string for singletons)
```

---

## 3. Geographic Distribution & Distribution Shift

- **Training Distribution**: Exclusively comprises records from the **United States (US)** and **India**.
- **Test Distribution Shift**: Introduces a significant volume of records from **France** (~12.8% of the test partition) in addition to US and India.
- **Architectural Handling**: Any pipeline utilizing fixed one-hot encoding or closed-set country dictionaries fails on test France records. Our pipeline utilizes open-set string normalization (`src/normalization.py::normalize_country`) and dynamic string agreement checks, handling France transparently.

---

## 4. Source Heterogeneity & Noise Profiles

| Feature / Aspect | Source 1 (Reference) | Source 2 (Partner A) | Source 3 (Partner B) |
| :--- | :--- | :--- | :--- |
| **Name Completeness** | $\sim 100\%$ | High ($\sim 98\%$) | Moderate ($\sim 85\%$) |
| **Name Form** | Canonical legal names | Legal / formal names | Trade names, DBAs, store #s |
| **Address Completeness**| $\sim 99\%$ | Sparse / Low ($\sim 35\%$) | High ($\sim 95\%$) |
| **Address Structure** | Standard street address | Often only city / state | Detailed street & suite #s |
| **Internal Duplication**| Zero (deduplicated) | Uncurated | Uncurated |

---

## 5. Ethical & Privacy Considerations

- **Synthetic / Anonymized Data**: Datasets are provided for competition research purposes and contain commercial business metadata rather than personal consumer information.
- **Zero Sensitive Attributes**: No protected attributes (race, gender, sexual orientation, medical history) exist within the business listing records.
