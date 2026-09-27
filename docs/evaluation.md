# Evaluation & Scoring Metrics

This document formalizes the official competition evaluation metric, **Macro $F_{0.5}$**, as implemented in `src/metrics.py`, detailing singleton edge cases, worked examples, and candidate generation metrics.

---

## 1. Official Metric: Macro-Averaged $F_{0.5}$

Evaluation is performed per Source 1 entity, and then macro-averaged across all reference entities:

$$\text{Macro } F_{0.5} = \frac{1}{|\mathcal{S}_1|} \sum_{e \in \mathcal{S}_1} F_{0.5}(e)$$

For a single Source 1 entity $e$:
- Let $T(e)$ be the set of true matching entity IDs from Source 2 and Source 3.
- Let $P(e)$ be the set of predicted matching entity IDs.

### Component Formulas:
$$\text{Precision}(e) = \frac{|T(e) \cap P(e)|}{|P(e)|}$$

$$\text{Recall}(e) = \frac{|T(e) \cap P(e)|}{|T(e)|}$$

$$F_{0.5}(e) = \frac{(1 + \beta^2) \times \text{Precision}(e) \times \text{Recall}(e)}{\beta^2 \times \text{Precision}(e) + \text{Recall}(e)} \quad (\text{where } \beta = 0.5)$$

Expanding $\beta = 0.5$ ($\beta^2 = 0.25$):
$$F_{0.5}(e) = \frac{1.25 \times \text{Precision}(e) \times \text{Recall}(e)}{0.25 \times \text{Precision}(e) + \text{Recall}(e)}$$

---

## 2. Singleton & Empty Set Scoring Rules

In real-world data, many entities have **no matching records** in other sources (singletons). The challenge defines strict scoring rules for these edge cases:

| True Set $T(e)$ | Predicted Set $P(e)$ | $F_{0.5}(e)$ Score | Rationale |
| :---: | :---: | :---: | :--- |
| $\emptyset$ (Empty) | $\emptyset$ (Empty) | **`1.0`** | Correctly identified singleton (true negative link). |
| $\emptyset$ (Empty) | Non-empty | **`0.0`** | False positive merge on a singleton. Severely penalized. |
| Non-empty | $\emptyset$ (Empty) | **`0.0`** | Failed to discover any true matches (zero recall). |
| Non-empty | Non-empty | $F_{0.5}$ formula | Standard evaluation if $|T \cap P| > 0$; $0.0$ if disjoint. |

---

## 3. Official Worked Example Verification

Consider the worked example provided in the challenge specification:

```python
from src.metrics import compute_macro_f05

# Example cases:
# Entity 1: True = {s2_1, s3_1}, Pred = {s2_1} -> P = 1.0, R = 0.5, F0.5 = 0.8333
# Entity 2: True = {}, Pred = {}              -> F0.5 = 1.0
# Entity 3: True = {s2_2}, Pred = {s2_3}       -> P = 0.0, R = 0.0, F0.5 = 0.0
# Entity 4: True = {}, Pred = {s3_2}          -> F0.5 = 0.0
```

Calculating Macro $F_{0.5}$:
$$\text{Macro } F_{0.5} = \frac{0.8333 + 1.0 + 0.0 + 0.0}{4} = 0.4583$$

This exact calculation is verified in our automated test suite (`tests/test_metrics.py::test_official_worked_example`).

---

## 4. Candidate Generation Metrics

In addition to matching accuracy, candidate blocking quality is evaluated using:

### 1. Candidate Blocking Recall
$$\text{Recall}_{\text{blocking}} = \frac{\sum_{e} |T(e) \cap \mathcal{C}(e)|}{\sum_{e} |T(e)|}$$
- Measures the fraction of true matches retained in the candidate pool.
- Our pipeline achieves: **`87.54%`**.

### 2. Search Space Reduction Ratio ($RR$)
$$RR = 1 - \frac{\sum_{e} |\mathcal{C}(e)|}{|\mathcal{S}_1| \times (|\mathcal{S}_2| + |\mathcal{S}_3|)}$$
- Measures the proportion of Cartesian pairs eliminated before scoring.
- Our pipeline achieves: **`99.9617%`**.

### 3. Average Candidates per S1
$$\bar{K} = \frac{1}{|\mathcal{S}_1|} \sum_{e \in \mathcal{S}_1} |\mathcal{C}(e)|$$
- Measures the efficiency of the candidate pool.
- Our pipeline averages: **`24.47`** candidates per entity (well within the max $50$ limit).
