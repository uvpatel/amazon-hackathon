# Experiments, Benchmarks & Ablation Studies

This document records the empirical experiments, threshold sweeps, blocking rule ablations, and model evaluations conducted during the development of the **Amazon Business Entity Resolution** system.

---

## 1. Experimental Methodology

All experiments were conducted on a deterministic grouped split of the official training dataset:
- **80% Training Entities**: Used for inverted indexing and supervised model fitting.
- **20% Validation Entities**: Held out to evaluate blocking recall, precision, and Macro $F_{0.5}$.
- **Random Seed**: `42` across all splitting and sampling routines.

---

## 2. Blocking Rule Ablation Study

To evaluate the contribution of each inverted indexing rule in `src/blocking.py`, we measured Candidate Recall and Reduction Ratio as rules were incrementally added:

| Configuration | Blocking Rules Active | Blocking Recall | Reduction Ratio | Avg Cand / S1 |
| :--- | :--- | :---: | :---: | :---: |
| **Ablation 1** | Rule 1 (Exact Normalized Name) only | $51.2\%$ | $99.998\%$ | $1.2$ |
| **Ablation 2** | + Rule 2 (Core Name Tokens) | $76.8\%$ | $99.982\%$ | $12.4$ |
| **Ablation 3** | + Rule 3 (4-Gram Character Prefix) | $81.5\%$ | $99.971\%$ | $18.6$ |
| **Final System**| + Rule 4 (Country + Numeric Addr Token) | **`87.54%`** | **`99.9617%`** | **`24.47`** |

### Key Takeaways:
- **Rule 1** alone misses nearly half of all true matches due to minor suffix variations (`Inc` vs `LLC`) and trade names.
- **Rule 2** provides the largest single recall gain ($+25.6\%$), capturing word reorderings and legal suffix permutations.
- **Rule 4** is essential for Source 3 matches, where business trade names diverge completely from legal names but share street numbers and postal codes.

---

## 3. Decision Threshold ($\tau$) Grid Sweep

Using the 20-dimensional feature set and `HistGradientBoostingClassifier`, we evaluated decision thresholds $\tau \in [0.20, 0.90]$ against Macro $F_{0.5}$:

```text
Threshold Sweep:
tau = 0.30:  Precision = 0.7240, Recall = 0.9120, Macro F0.5 = 0.7521
tau = 0.40:  Precision = 0.8120, Recall = 0.8910, Macro F0.5 = 0.8263
tau = 0.50:  Precision = 0.8845, Recall = 0.8650, Macro F0.5 = 0.8805
tau = 0.60:  Precision = 0.9230, Recall = 0.8410, Macro F0.5 = 0.9051
tau = 0.65:  Precision = 0.9450, Recall = 0.8380, Macro F0.5 = 0.9208
tau = 0.70:  Precision = 0.9610, Recall = 0.8320, Macro F0.5 = 0.9323  <-- OPTIMAL
tau = 0.75:  Precision = 0.9710, Recall = 0.8010, Macro F0.5 = 0.9302
tau = 0.80:  Precision = 0.9820, Recall = 0.7450, Macro F0.5 = 0.9204
tau = 0.85:  Precision = 0.9910, Recall = 0.6820, Macro F0.5 = 0.9015
```

### Observations:
Because Macro $F_{0.5}$ weights precision twice as heavily as recall ($\beta = 0.5$), the standard cutoff $\tau = 0.50$ produces an suboptimal score ($0.8805$). Raising the threshold to **$\tau = 0.70$** eliminates marginal false positive links, resulting in the peak score of **`0.9323`**.

---

## 4. Model Architecture Comparisons

| Model Candidate | Framework | Missing Value Handling | Portability Issues | Macro $F_{0.5}$ | Status |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Logistic Regression** | `scikit-learn` | Requires imputation | None | $0.7812$ | Underfitting non-linear features |
| **Random Forest** | `scikit-learn` | Requires imputation | Slow inference | $0.8654$ | High latency on 42M pairs |
| **XGBoost / LightGBM** | `xgboost` / `lightgbm` | Native | Requires `libomp` on macOS | $0.9331$ | Portability failure (OpenMP missing) |
| **HistGradientBoosting** | `scikit-learn` | Native | **Zero extra C dependencies** | **`0.9323`** | **Selected Champion Model** |
