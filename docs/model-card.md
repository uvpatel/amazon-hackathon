# Model Card: HistGradientBoosting Business Entity Matcher

Following the standard Model Card specification (Mitchell et al., 2019), this document provides comprehensive model details, intended uses, evaluation results, and ethical considerations.

---

## 1. Model Details

- **Model Name**: HistGradientBoosting Business Entity Matcher
- **Architecture**: Gradient Boosted Decision Tree (`sklearn.ensemble.HistGradientBoostingClassifier`)
- **Version**: 1.0.0
- **Release Date**: September 27, 2026
- **Developers**: Team Deadly Trio (Urvil Patel & Megh Patel)
- **License**: Apache 2.0 / BSD 3-Clause compatible
- **Parameter Count**: $\ll 1\text{M}$ parameters (strictly complies with $\le 8\text{B}$ challenge limit)
- **Input**: 20-dimensional pairwise similarity feature vector $\mathbf{x} \in \mathbb{R}^{20}$
- **Output**: Match probability $P(\text{match} \mid \mathbf{x}) \in [0.0, 1.0]$

---

## 2. Intended Use

### Primary Intended Uses
- Deduplication and record linkage of noisy commercial business listings across independent enterprise databases.
- Resolving business entities in catalogs without global unique identifiers.
- Official participation in the Amazon ML Challenge 2026.

### Out-of-Scope Uses
- Individual personal identity resolution or facial/biometric matching.
- Real-time sub-millisecond transaction fraud detection (this pipeline is engineered for batched catalog reconciliation).
- Matching records across non-Latin scripts without prior transliteration.

---

## 3. Training Data & Supervision

- **Sources**:
  - Source 1: Clean, deduplicated reference business records.
  - Source 2 & 3: Noisy partner business records (United States & India).
- **Supervision**: `train_ground_truth.tsv` providing positive links between Source 1 and Source 2/3.
- **Negative Sampling**: Inverted index hard negatives combined with uniform background negatives.
- **Class Balancing**: `class_weight='balanced'` applied to mitigate the ~1:200 candidate class skew.

---

## 4. Evaluation & Quantitative Results

### Performance on Held-Out Validation Split:
- **Macro $F_{0.5}$**: **`0.9323`** (optimal cutoff $\tau = 0.70$)
- **Precision**: **`0.9610`**
- **Recall**: **`0.8320`**
- **Singleton Accuracy**: **`98.2%`**
- **Reduction Ratio**: **`99.9617%`**

### Official Submission Validator Status:
- **Status**: **`PASS`** (0 blocking issues, 0 warnings across 1.73M test records)

---

## 5. Ethical & Environmental Considerations

- **Compute Footprint**: The entire training pipeline executes in under 30 seconds on a standard commodity laptop CPU, using negligible electricity compared to multi-billion parameter LLMs.
- **Fairness & Bias**: Evaluated across multiple geographic regions (US, India, and France). The model relies on deterministic structural and token similarity metrics rather than demographic embeddings, avoiding racial or socioeconomic bias.
