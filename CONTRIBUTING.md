# Contributing Guidelines

Thank you for your interest in contributing to the **Amazon Business Entity Resolution** project. This document outlines our development process, coding standards, and pull request procedures.

---

## 1. Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.

---

## 2. Getting Started

### Prerequisites
- Python 3.9+ (tested on Python 3.14.6)
- Git

### Local Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/uvpatel/amazon-hackathon.git
   cd amazon-hackathon
   ```
2. Set up a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r code/business_entity_resolution/requirements.txt
   ```

---

## 3. Development Workflow

1. **Branching Strategy:**
   - Create a feature or bugfix branch off `main`:
     ```bash
     git checkout -b feature/your-feature-name
     # or
     git checkout -b fix/your-bugfix-name
     ```
2. **Commit Conventions:**
   - Write clear, imperative commit messages (e.g., `feat: add phonetic blocking rule`, `fix: address empty string edge case in normalizer`).
3. **Data Handling & Fair Play (CRITICAL):**
   - **DO NOT commit challenge dataset files** (`*.tsv` in `student_resource/dataset/`). These are strictly git-ignored.
   - **DO NOT integrate external lookup APIs**, web scrapers, or third-party geocoding tools. All matching must be strictly local and self-contained.
4. **Testing Requirements:**
   - Run the complete test suite before opening a pull request:
     ```bash
     python3 -m pytest tests/ -v
     ```
   - If adding new features or normalization rules, add corresponding unit tests under `tests/`.

---

## 4. Code Standards & Best Practices

- **Type Annotations:** Use Python type hints (`typing.Dict`, `typing.List`, `typing.Set`, `typing.Tuple`, `typing.Optional`) on public functions.
- **Contract Integrity:**
  - Preserving TSV delimiters (`sep="\t"`).
  - Enforce explicit `keep_default_na=False` and string types (`dtype=str`) for all entity IDs.
  - Maintain the candidate boundary invariant: `matched_entity_ids ⊆ candidate_entity_ids`.
- **Reproducibility:** Fix random seeds (default: `42`) across models and cross-validation splits.

---

## 5. Submitting a Pull Request

Before submitting:
- [ ] Automated tests pass (`python3 -m pytest tests/ -v`).
- [ ] Code follows project formatting and typing conventions.
- [ ] Documentation has been updated to reflect code changes.
- [ ] No sensitive credentials, private paths, or raw challenge datasets are included.
- [ ] PR description clearly explains the changes, motivation, and test evidence.
