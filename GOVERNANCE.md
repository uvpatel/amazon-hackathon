# Project Governance

This document describes the governance model and decision-making framework for the **Amazon Business Entity Resolution** codebase.

## 1. Project Overview & Scope

This project is an open-source machine learning system developed for the Amazon ML Challenge 2026. The scope includes:
- Multi-source entity resolution algorithms (blocking, indexing, normalization).
- Pairwise feature extraction and gradient-boosted binary classification.
- High-throughput streaming batch inference for millions of records.
- Challenge compliance, validation, and reproducible evaluation.

## 2. Maintainer Model

The project operates under a maintainer-driven governance structure. The active core maintainers are:

- **Urvil Patel** (`uvpatel7271@gmail.com`) — Core Maintainer & Architectural Lead
- **Megh Patel** (`meghpatel0009@gmail.com`) — Core Maintainer & ML Modeling Lead

### Responsibilities of Maintainers
1. **Repository Integrity**: Ensuring the master branch remains stable, dependencies remain minimal and open-source compliant, and all automated tests pass.
2. **Architecture Decisions**: Reviewing architectural changes, algorithmic modifications, or dependency additions via Architecture Decision Records (ADRs).
3. **Security & Vulnerabilities**: Triaging security reports in accordance with [SECURITY.md](SECURITY.md).
4. **Code Reviews**: Reviewing pull requests against the acceptance criteria outlined in [CONTRIBUTING.md](CONTRIBUTING.md).

## 3. Decision-Making Process

- **Consensus-Driven**: Technical proposals, refactoring efforts, and architectural decisions are made by consensus among core maintainers.
- **Spec-Driven Evolution**: Major architectural shifts require an Architecture Decision Record (ADR) stored in `docs/decisions/`.
- **Challenge Invariants**: No decision may violate non-negotiable challenge constraints (e.g., TSV format, subset invariant `matches ⊆ candidates`, open-set country representation, no external network calls).

## 4. Conflict Resolution

If consensus cannot be reached on a technical matter:
1. An empirical benchmark or test is constructed to evaluate alternatives quantitatively (e.g., impact on Macro F0.5, runtime latency, or memory consumption).
2. The alternative that scores higher on Macro F0.5 without violating reproducibility or memory constraints is adopted.
3. If scores are tied, the simpler implementation with fewer dependencies is selected.
