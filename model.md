# Model Card: HistGradientBoosting Business Entity Matcher

This document summarizes the machine learning model architecture. For the complete, detailed specification, see [docs/model-card.md](docs/model-card.md).

- **Architecture**: `sklearn.ensemble.HistGradientBoostingClassifier`
- **Trained Artifact**: `output/model.pkl`
- **Optimal Decision Threshold**: $\tau = 0.70$
- **Feature Vector**: 20-dimensional pairwise similarity features (lexical, token, numeric, country, missingness)
- **Validation Macro $F_{0.5}$**: **`0.9323`**
- **Blocking Recall**: **`87.54%`**
- **Reduction Ratio**: **`99.9617%`**
- **Official Validator Status**: **`PASS`**
