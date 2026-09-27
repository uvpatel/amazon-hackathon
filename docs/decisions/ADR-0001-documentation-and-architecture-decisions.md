# ADR-0001: Architecture, Model Selection, Metrics, and Documentation Strategy

## Status
**Accepted** (2026-09-27)

## Context
The Amazon ML Challenge 2026 requires an end-to-end machine learning system capable of resolving millions of noisy business entity records across three distinct sources without common identifiers. The solution must adhere strictly to challenge constraints:
1. Permissible open-source license (MIT / Apache 2.0).
2. Parameter count strictly $\le 8\text{B}$.
3. Zero external internet lookups, geocoding APIs, or third-party web services.
4. Strict TSV input and output formatting.
5. Macro $F_{0.5}$ metric optimization, which weights Precision $2\times$ over Recall.
6. The candidate set must be frozen and output as `candidate_pairs.tsv`, with the invariant that `matched_entity_ids` $\subseteq$ `candidate_entity_ids`.
7. Out-of-the-box cross-platform portability (Linux, macOS, Windows).

During initial reconnaissance, multiple engineering trade-offs required explicit decisions:
- Choice of gradient boosting engine: `LightGBM` / `XGBoost` vs `HistGradientBoostingClassifier`.
- String similarity library: `rapidfuzz` / C-extensions vs pure Python standard library (`difflib`, `re`).
- Streaming memory strategy vs in-memory materialization for 1.73M records.
- Comprehensive documentation architecture and open-source licensing.

---

## Decisions

### 1. Model Engine: Scikit-Learn `HistGradientBoostingClassifier`
- **Decision**: Adopt Scikit-Learn's `HistGradientBoostingClassifier` instead of external XGBoost or LightGBM packages.
- **Rationale**:
  - LightGBM and XGBoost failed to execute on macOS developer environments due to missing OpenMP C++ runtime libraries (`libomp.dylib`).
  - `HistGradientBoostingClassifier` uses integer histogram binning (inspired by LightGBM), handles missing feature values natively without imputation, and requires zero external C runtime libraries.
  - It comfortably satisfies the $\le 8\text{B}$ parameter constraint ($\ll 1\text{M}$ parameters) and permissively ships under BSD/Apache licenses.

### 2. Feature Extraction: Pure Python & NumPy Similarity Functions
- **Decision**: Implement all token Jaccard, character sequence matching (`difflib.SequenceMatcher`), and numeric extraction functions in self-contained pure Python.
- **Rationale**:
  - Avoids external C-bindings (`rapidfuzz`, `jellyfish`) that introduce wheel compilation errors across different operating systems and CPU architectures.
  - Guarantees 100% deterministic reproducibility across Python versions.

### 3. Candidate Boundary Snapshot Invariant
- **Decision**: Candidate sets retrieved from the multi-rule inverted index are snapshotted and written to `output/candidate_pairs.tsv` directly before pairwise feature extraction and model scoring.
- **Rationale**:
  - The official submission validator rigorously enforces that all predicted matches belong to the candidate set: $\text{matches} \subseteq \text{candidates}$.
  - Deriving match predictions exclusively by applying the decision threshold $\tau$ to the scored candidates mathematically guarantees compliance with this invariant.

### 4. Decision Threshold Calibration: $\tau = 0.70$
- **Decision**: Calibrate the classification decision cutoff to $\tau = 0.70$ rather than the default $\tau = 0.50$.
- **Rationale**:
  - Macro $F_{0.5}$ penalizes false positive merges twice as heavily as false negatives.
  - Empirical grid evaluation on the held-out validation split proved that $\tau = 0.70$ maximized Macro $F_{0.5}$ to $0.9323$ while keeping false positive merges near zero.

### 5. Open-Set Country Representation
- **Decision**: Represent countries as canonicalized open strings rather than categorical one-hot encodings.
- **Rationale**:
  - The test dataset introduces France (~12.8% of test records), which was completely absent in the training set (US and India).
  - Categorical or one-hot encoders trained on US/India crash or discard France. Open-set string comparison $\mathbb{I}(c_1 == c_2)$ operates seamlessly on any country code.

### 6. Documentation Suite Architecture
- **Decision**: Create a comprehensive, discoverable, GitHub-ready technical documentation suite under `docs/`, featuring an ADR directory, model card, dataset card, and step-by-step guides reconciled with existing project specs.
- **Rationale**:
  - Ensures full transparency, rapid developer onboarding, clear governance, and reproducible research standards.

---

## Consequences

### Positive
- Zero external native dependencies: Installs and runs smoothly across macOS, Linux, and Windows.
- 100% compliant with the official challenge validator (`PASS` on 1.73M records).
- Peak memory during full-test inference is bounded under $4\text{ GB}$ via streaming batching.
- High Precision and Macro $F_{0.5}$ score of $0.9323$.

### Negative / Trade-Offs
- `difflib.SequenceMatcher` is slower than compiled C++ string similarity libraries. Full inference over 1.73M test records takes ~20 minutes on an 8-core CPU.
- Candidate cap at $K = 50$ trades a slight potential loss in recall for constant memory and predictable latency bounds.
