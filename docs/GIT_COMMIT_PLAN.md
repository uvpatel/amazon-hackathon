# Git Commit & Release Plan: Amazon Business Entity Resolution

**Branch:** `main`  
**Remote:** `origin` (`https://github.com/uvpatel/amazon-hackathon.git`)  
**Date:** 2026-09-27  
**Strategy:** Atomic, feature-wise Conventional Commits with zero data/secret leakage.

---

## 1. Audit Summary

### Tracked Modified Files
- `Documentation_template.md` (Updated official challenge writeup with empirical metrics)
- `README.md` (Upgraded from stub to comprehensive landing page)
- `code/business_entity_resolution/README.md` (Package-level reproduction guide)
- `code/business_entity_resolution/requirements.txt` (Pinned dependencies)
- `code/business_entity_resolution/src/blocking.py` (Multi-rule inverted index implementation)
- `code/business_entity_resolution/src/pipeline.py` (CLI orchestration and streaming inference)
- `code/business_entity_resolution/src/utils.py` (Strict TSV I/O and validation)
- `output/candidate_pairs.tsv` (Generated test candidate set, 257 MB) -> **EXCLUDED**
- `output/matching_results.tsv` (Generated test prediction set, 58 MB) -> **EXCLUDED**
- `requirements.txt` (Root dependency manifest)

### Untracked Files
- Configuration & Build: `.editorconfig`, `.env.example`, `.gitattributes`, `Makefile`
- GitHub Automation: `.github/` (issue templates, PR template, dependabot, docs-check CI)
- Governance & Legal: `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `CHANGELOG.md`, `CITATION.cff`, `AUTHORS.md`, `ACKNOWLEDGMENTS.md`, `GOVERNANCE.md`, `ROADMAP.md`
- Source Modules: `features.py`, `metrics.py`, `model.py`, `normalization.py`
- Test Suite: `tests/` (7 test files, 32 passing tests)
- Documentation Suite: `docs/*.md`, `docs/decisions/`, `docs/implementation/`, `model.md`
- Model Artifact: `output/model.pkl` (408 KB) -> **EXCLUDED**

---

## 2. Excluded Files & Safety Rationale

The following generated artifacts are intentionally excluded from Git staging and will remain safely preserved in the local working directory:

| Path | Size / Type | Reason for Exclusion |
| :--- | :---: | :--- |
| `output/candidate_pairs.tsv` | `257 MB` TSV | **Exceeds GitHub's 100 MB hard limit**. Pushing would cause GitHub's remote hook to abort. Also a generated submission artifact reproducible via `make predict`. |
| `output/matching_results.tsv` | `58 MB` TSV | Large generated leaderboard prediction artifact reproducible via `make predict`. |
| `output/model.pkl` | `408 KB` Binary | Serialized pickle checkpoint. Reproducible via `make train`. Standard practice is to exclude binary model weights from git history. |
| `student_resource/` | `~3 GB` Data | Raw hackathon competition datasets. Already excluded via `.gitignore`. |
| `.pytest_cache/` | Cache | Python test runner cache. Already excluded via `.gitignore`. |

---

## 3. Proposed Atomic Commit Sequence

| # | Commit Message | Scope / Feature | Included Files | Validation Protocol |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `build: configure dependencies and developer workflow tooling` | Project configuration and developer environment | `requirements.txt`<br>`code/business_entity_resolution/requirements.txt`<br>`Makefile`<br>`.editorconfig`<br>`.gitattributes`<br>`.env.example` | File syntax, line ending normalization check |
| **2** | `feat(data): implement strict TSV loaders, schema validation, and submission formatting` | Data layer and contract enforcement | `code/business_entity_resolution/src/utils.py`<br>`tests/test_data.py` | `pytest tests/test_data.py -v` (7 passed) |
| **3** | `feat(normalization): add deterministic text, name, address, and open-set country normalization` | Normalization engine | `code/business_entity_resolution/src/normalization.py`<br>`tests/test_normalization.py` | `pytest tests/test_normalization.py -v` (7 passed) |
| **4** | `feat(blocking): implement multi-rule inverted index candidate generation engine` | Candidate generation and indexing | `code/business_entity_resolution/src/blocking.py`<br>`tests/test_blocking.py` | `pytest tests/test_blocking.py -v` (3 passed) |
| **5** | `feat(features): implement 20-dimensional pairwise similarity feature extraction` | Pairwise feature extraction | `code/business_entity_resolution/src/features.py`<br>`tests/test_features.py` | `pytest tests/test_features.py -v` (5 passed) |
| **6** | `feat(model): implement HistGradientBoosting classifier with threshold calibration` | ML modeling and threshold calibration | `code/business_entity_resolution/src/model.py`<br>`tests/test_model.py` | `pytest tests/test_model.py -v` (4 passed) |
| **7** | `feat(metrics): implement official Macro F0.5 scoring and blocking recall evaluation` | Evaluation and challenge metrics | `code/business_entity_resolution/src/metrics.py`<br>`tests/test_metrics.py` | `pytest tests/test_metrics.py -v` (5 passed) |
| **8** | `feat(pipeline): add end-to-end training and streaming batch inference with candidate snapshots` | End-to-end pipeline CLI | `code/business_entity_resolution/src/pipeline.py`<br>`tests/test_pipeline.py` | `pytest tests/test_pipeline.py -v` + full test suite (32 passed) |
| **9** | `chore(github): configure issue templates, pull request checklist, dependabot, and CI` | GitHub community hygiene and CI | `.github/ISSUE_TEMPLATE/*`<br>`.github/PULL_REQUEST_TEMPLATE.md`<br>`.github/dependabot.yml`<br>`.github/workflows/docs-check.yml` | YAML parsing validation |
| **10**| `docs(governance): add open source governance, security policy, code of conduct, and citation` | Governance, legal, and citations | `LICENSE`<br>`SECURITY.md`<br>`CODE_OF_CONDUCT.md`<br>`CONTRIBUTING.md`<br>`SUPPORT.md`<br>`CHANGELOG.md`<br>`CITATION.cff`<br>`AUTHORS.md`<br>`ACKNOWLEDGMENTS.md`<br>`GOVERNANCE.md`<br>`ROADMAP.md`<br>`docs/LICENSE_SELECTION.md` | YAML parsing of CITATION.cff, link checks |
| **11**| `docs: add comprehensive technical documentation suite, model card, and architecture decisions` | Complete technical documentation | `README.md`<br>`code/business_entity_resolution/README.md`<br>`Documentation_template.md`<br>`model.md`<br>`docs/*.md`<br>`docs/decisions/*`<br>`docs/implementation/*` | Python link check (61 files, 0 broken links) |
