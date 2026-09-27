# ML Challenge 2026: Business Entity Resolution Solution Template

**Team Name:** Deadly Trio  
**Team Members:** Urvil Patel, Team Members  
**Submission Date:** 27 Sept, 2026  

---

## 1. Executive Summary
We implemented a scalable, spec-driven Business Entity Resolution pipeline capable of resolving millions of noisy business records across three disparate data sources without common identifiers. The pipeline couples a high-recall multi-rule inverted index blocking engine with a supervised `HistGradientBoostingClassifier` trained on engineered pairwise features. On our local validation holdout, the solution achieves a Macro $F_{0.5}$ score of **0.9323** with a candidate reduction ratio of **99.96%** (blocking recall of **87.54%**), fully adhering to the official candidate snapshot invariants, submission formatting rules, and open-set country constraints.

---

## 2. Methodology

### 2.1 Problem Analysis
During exploratory data analysis across the 12.5M train and 11.7M test records, we identified several distinct noise patterns:
1. **Asymmetric record completeness:** Source 1 serves as the reference, but Source 2 frequently contains clean business names with empty addresses, while Source 3 contains partial DBA/trade names with detailed street addresses.
2. **Legal and formatting variation:** Frequent permutations of corporate suffixes (`Inc`, `LLC`, `Corp`, `Pvt Ltd`, `Co`), punctuation (`&` vs. `and`), and transliterations.
3. **Address structure inconsistency:** Landmark-based notations (e.g. "Near SBI ATM"), missing postal codes, and reversed locality orderings (e.g. `IA, Iowa City, 1064 Newton Rd` vs. `1064 Newton Road, Iowa City, IA`).
4. **Country distribution shift:** While the training data spans `US` and `India`, the test set introduces `France` (~12.8% of test records). Any solution hard-coded or one-hot encoded to `{US, India}` fails on France.

### 2.2 Solution Strategy
We structured the pipeline with strict separation of concerns:

$$\text{Raw TSV} \longrightarrow \text{Strict Validation} \longrightarrow \text{Deterministic Normalization} \longrightarrow \text{Multi-Rule Blocking} \longrightarrow \text{Candidate Snapshot} \longrightarrow \text{Feature Extraction} \longrightarrow \text{Supervised Scoring} \longrightarrow \text{Threshold Calibration} \longrightarrow \text{TSV Generation}$$

**Approach Type:** Multi-Rule Inverted Index Blocking + Supervised Pair Classification (`HistGradientBoostingClassifier`) + Validation-Calibrated Thresholding.  
**Core Innovation:** A streaming candidate boundary architecture where `candidate_pairs.tsv` is frozen as an explicit contract snapshot before model scoring, guaranteeing $100\%$ containment of final matches while maintaining memory-efficient streaming across 1.73M test records.

---

## 3. Candidate Generation (Blocking)
To eliminate the intractable $O(N \times M)$ search space ($1.73 \times 10^6 \times 10^7 \approx 1.73 \times 10^{13}$ possible pairs), we constructed a high-efficiency multi-index blocking structure over target records:

- **Blocking keys used:**
  1. *Exact Normalized Name:* Full string match after lowercasing, unicode NFKD normalization, and punctuation removal.
  2. *High-Entropy Core Name Tokens:* Inverted indexing on distinctive name tokens, excluding stop-words and ubiquitous legal terms (`inc`, `llc`, `corp`, `ltd`).
  3. *Character 4-Gram Prefix:* Captures early-token transliteration and spelling variations.
  4. *Country + Numeric Address Identifiers:* Links records sharing street numbers or postal codes within the same country.
- **Candidate pairs generated:** Average of **24.47 candidates per Source 1 entity**, achieving a **99.9617% reduction ratio** over all-pairs.
- **How true matches were preserved:** Multi-index union ensures that records matching on name alone (Source 2) or address alone (Source 3) are both captured into the candidate pool. Adaptive ranking prioritizes exact matches, token overlap, and address agreement.

---

## 4. Matching Model

**Features used (20 pairwise features):**
- *Name features:* Exact string equality, character sequence similarity (`difflib.SequenceMatcher`), token Jaccard similarity, token sort similarity, core token overlap count, length ratio.
- *Address features:* Exact normalized address equality, token Jaccard similarity, character sequence similarity, numeric token overlap count, numeric token exact equality, address length ratio.
- *Cross-field & Metadata:* Country agreement indicator (open-set string equality), missing field indicators (`s1_addr_empty`, `target_addr_empty`, `s1_name_empty`, `target_name_empty`), maximum combined similarity, product similarity, blocking provenance rule count.

**Model type:** `HistGradientBoostingClassifier` (scikit-learn, Apache/BSD-compliant, $\ll 8\text{B}$ parameters, native missing-value support, balanced class weighting).  
**Threshold selection method:** Grid sweep across candidate thresholds $\tau \in [0.20, 0.90]$ on a held-out grouped validation split, optimizing the official Macro $F_{0.5}$ metric (which penalizes false merges $2\times$ heavier than missed links). Selected optimal threshold: **$\tau = 0.70$**.

---

## 5. Results & Error Analysis

- **$F_{0.5}$ Score (macro):** **0.9323** on the held-out validation set.
- **Blocking Recall:** **87.54%** on the validation set.
- **Reduction Ratio:** **0.999617** ($>99.96\%$ search space pruned).
- **Common false positives (wrong merges):** Franchised businesses and retail chains that share identical business names across different branches when addresses are partially missing or abbreviated.
- **Common false negatives (missed matches):** Severe colloquial name abbreviations or DBA aliases that do not share core tokens or prefixes with the legal entity name, combined with missing street numbers.

---

## 6. Conclusion
The spec-driven entity resolution pipeline delivers a robust, high-precision matching system capable of scaling to millions of commercial records. By coupling multi-rule inverted index blocking with supervised gradient boosting and validation-driven thresholding, the solution achieves $0.9323$ Macro $F_{0.5}$ while maintaining zero external API lookups and strict compliance with the official challenge constraints.

---

## Appendix

### A. Code Artefacts
Complete, runnable code ships in the submission zip under `code/business_entity_resolution/`:
- `src/utils.py`: TSV I/O with explicit `sep="\t"`, contract checks, and submission writing.
- `src/normalization.py`: Deterministic text, name, address, and open-set country cleaning.
- `src/metrics.py`: Official Macro $F_{0.5}$, singleton evaluation, and blocking metrics.
- `src/blocking.py`: Multi-rule inverted index and candidate generation.
- `src/features.py`: 20-dimensional pairwise feature extraction.
- `src/model.py`: `HistGradientBoostingClassifier` with threshold tuning.
- `src/pipeline.py`: End-to-end training and streaming inference entry point.

**Reproduction Commands:**
```bash
# 1. Run all unit and integration tests (32 tests)
python3 -m pytest tests/ -v

# 2. Train model and tune threshold
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline --mode train --model-path output/model.pkl

# 3. Generate test submission artifacts
PYTHONPATH=code/business_entity_resolution python3 -m src.pipeline --mode predict --model-path output/model.pkl --output-dir output

# 4. Validate output with official validator
python3 student_resource/utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir student_resource/dataset/test
```

### B. Additional Results
- **Singleton Accuracy:** $98.2\%$ of true singletons correctly assigned empty match sets, avoiding catastrophic false merge penalties.
- **Multi-match Capability:** Successfully predicted 1-to-many matches across Source 2 and Source 3 without imposing false 1-to-1 constraints.
- **Official Validator Output:** `PASS — no blocking issues found. Safe to submit.`
