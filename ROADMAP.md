# Project Roadmap

This roadmap documents the completed milestones for the Amazon ML Challenge 2026, as well as planned enhancements for future iterations of this entity resolution system.

---

## 1. Completed Milestones (Hackathon Delivery)

- [x] **Phase 1: Spec-Driven Architecture & Contracts**
  - Formalized schemas for Source 1, 2, 3 and Ground Truth (`docs/01_system_spec.md`, `docs/02_data_contract.md`).
  - Implemented strict TSV I/O with explicit tab delimiter enforcement and error handling.
- [x] **Phase 2: Normalization & Preprocessing**
  - Implemented deterministic unicode normalization (NFKD), punctuation strip, and lowercase conversion.
  - Built legal business suffix standardization (`Inc`, `LLC`, `Corp`, `Pvt Ltd`).
  - Built address token normalization and street abbreviations (`St`, `Rd`, `Ave`, `Blvd`).
  - Implemented open-set country string normalization supporting US, India, France, and arbitrary novel ISO codes.
- [x] **Phase 3: Multi-Rule Blocking Engine**
  - Engineered 4-tier inverted index: Exact normalized name, high-entropy core tokens, character 4-gram prefixes, and numeric token + country keys.
  - Achieved $99.9617\%$ search space reduction with $87.54\%$ blocking recall.
- [x] **Phase 4: Pairwise Feature Engineering**
  - Implemented 20 pairwise similarity metrics (pure Python + NumPy, avoiding external C-bindings).
  - Lexical, token Jaccard, character sequence matcher, address numeric overlap, country agreement, and missingness indicators.
- [x] **Phase 5: Supervised Matching & Calibration**
  - Implemented `HistGradientBoostingClassifier` with balanced class weighting.
  - Calibrated decision threshold on held-out S1 validation split to $\tau = 0.70$, optimizing Macro $F_{0.5} = 0.9323$.
- [x] **Phase 6: Streaming Inference & Verification**
  - Built memory-bounded streaming batch inference producing `output/candidate_pairs.tsv` and `output/matching_results.tsv`.
  - Guaranteed `matched_entity_ids ⊆ candidate_entity_ids` invariant.
  - Passed official submission validator (`student_resource/utils/validate_submission.py --check-ids`).
- [x] **Phase 7: Test Suite & Documentation**
  - 32 automated unit and integration tests passing in $1.24\text{s}$.
  - Comprehensive documentation suite, model card, dataset card, and audit.

---

## 2. Planned Enhancements (Post-Hackathon)

### Near-Term (v1.1)
- [ ] **Multi-processing in Streaming Inference**:
  - Parallelize candidate generation across CPU cores using Python's `multiprocessing.Pool` or `ProcessPoolExecutor` to reduce inference time on massive datasets ($>10\text{M}$ records) from 20 minutes to $<5$ minutes.
- [ ] **Enhanced Transliteration Engine**:
  - Incorporate unidecode or dedicated multilingual phonetic hashing (e.g., Double Metaphone or Soundex adapted for Indian and French names) to improve recall on phonetic misspellings.
- [ ] **Adaptive Per-Source Thresholds**:
  - Explore learning separate decision thresholds $\tau_{S2}$ and $\tau_{S3}$ to account for asymmetric noise profiles between Source 2 (name-heavy) and Source 3 (address-heavy).

### Mid-Term (v1.2)
- [ ] **Embedding-Based Annoy / FAISS Blocking**:
  - Add optional vector-based approximate nearest neighbor (ANN) blocking using open-source sentence-transformers (e.g., `all-MiniLM-L6-v2`) while preserving the $\le 8\text{B}$ parameter limit and sub-quadratic candidate generation.
- [ ] **Graph Connected Components / Transitive Closure**:
  - In scenarios where cross-source links imply transitive relationships ($S1 \sim S2$ and $S1 \sim S3$), implement graph-based cluster validation to prune conflicting multi-match assignments.

### Long-Term (v2.0)
- [ ] **Active Learning & Incremental Refinement**:
  - Web UI for human-in-the-loop review of borderline candidate pairs ($\tau \in [0.65, 0.75]$) with active learning updates to the boosting model.
- [ ] **Distributed Execution via Apache Spark / Ray**:
  - Scale blocking and feature generation pipelines to hundreds of millions of international business records in a distributed cluster.
