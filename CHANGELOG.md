# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Complete spec-driven Entity Resolution pipeline:
  - Strict TSV data layer and contract validation (`src/utils.py`).
  - Deterministic name, address, and open-set country normalization engine (`src/normalization.py`).
  - Official Macro-averaged F0.5 metric with full singleton credit (`src/metrics.py`).
  - Multi-rule inverted index blocking engine (`src/blocking.py`).
  - Vectorized 20-dimensional pairwise feature extractor (`src/features.py`).
  - Supervised `HistGradientBoostingClassifier` with validation threshold tuning (`src/model.py`).
  - End-to-end batched streaming inference engine (`src/pipeline.py`).
- 32 comprehensive unit and integration tests across data, normalization, metrics, blocking, features, model, and pipeline (`tests/`).
- Full submission output artifacts:
  - `output/matching_results.tsv` (1,732,544 test entities scored).
  - `output/candidate_pairs.tsv` (1,732,544 test candidate sets).
  - `output/model.pkl` (trained model artifact).
- Verified official submission validator status: `PASS` across full test dataset and 9.97M valid target IDs.
- Comprehensive technical documentation suite in `docs/` and root GitHub health files (`SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SUPPORT.md`).

---

## [0.1.0] - 2026-09-27

### Added
- Initial project structure for Amazon ML Challenge 2026 (`f54872f`).
- Repository `.gitignore` rules (`1b3d464`).
- Official solution documentation template (`0d372a6`).
- Hackathon problem statement and guidelines (`328e206`).
- Spec-driven engineering architecture documents (`300f412`).
