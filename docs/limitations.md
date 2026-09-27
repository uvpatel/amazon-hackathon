# System Limitations & Edge Cases

This document describes the inherent performance boundaries, known failure modes, and architectural trade-offs of the **Amazon Business Entity Resolution** system.

---

## 1. Algorithmic Boundaries & Known Failure Modes

### A. Severe Colloquial Abbreviations & Acronyms
- **Limitation**: When a trade name (Source 3) consists solely of an acronym or arbitrary pseudonym that shares zero core tokens, 4-gram prefixes, or numeric address tokens with the legal entity name (e.g. `KFC` vs `Kentucky Fried Chicken`, where the address is also corrupted or missing).
- **Impact**: Such pairs are not indexed into the candidate pool during blocking, causing false negatives (missed matches).

### B. High-Density Franchise / Retail Chains
- **Limitation**: Large national chains (e.g., `Subway`, `McDonald's`, `Starbucks`) with thousands of retail locations across identical cities where street addresses are omitted or abbreviated.
- **Impact**: The model may face ambiguity distinguishing between different physical branch locations if street numbers are missing, occasionally causing false positive merges.

### C. Open-Set Language Transliteration
- **Limitation**: While NFKD unicode normalization removes accents and diacritics, it does not perform phonetic or semantic transliteration between scripts (e.g. Devanagari to Latin).
- **Impact**: Entities whose names are entirely in non-Latin scripts without English transliteration in one source cannot be matched via Latin character n-grams.

---

## 2. Resource & Scalability Boundaries

### A. Single-Threaded Streaming Inference
- **Current State**: Candidate generation and streaming inference currently execute in a single Python thread.
- **Scalability**: While memory is strictly bounded ($<4\text{ GB}$), processing $1,732,544$ records takes approximately $20\text{ minutes}$ on a modern 8-core CPU.
- **Future Mitigation**: Parallelizing batch candidate retrieval using `multiprocessing.Pool` (planned for v1.1).

### B. Top-K Candidate Cap ($K = 50$)
- **Current State**: Candidate lists per Source 1 entity are truncated at the top 50 candidates.
- **Trade-Off**: In rare cases where an entity has more than 50 plausible candidates in the target pool, true matches ranked $>50$ will be omitted from scoring to protect memory and inference latency.

---

## 3. Challenge Rules & Operational Constraints

1. **No External Lookups**: The pipeline does not and cannot query external search engines, corporate registries (e.g., OpenCorporates, SEC EDGAR), or geocoding services (e.g., Google Maps API). All resolution is strictly derived from the provided tabular data.
2. **Model Parameter Limit**: Restricted to $\le 8\text{B}$ parameters. Our gradient booster uses $\ll 1\text{M}$ parameters, comfortably adhering to this limit.
