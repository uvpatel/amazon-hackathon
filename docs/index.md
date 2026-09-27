# Documentation Portal & Technical Sitemap

Welcome to the technical documentation for the **Amazon Business Entity Resolution** system developed for the Amazon ML Challenge 2026 by team **Deadly Trio** (Urvil Patel and Megh Patel).

This documentation provides complete coverage of our end-to-end entity matching pipeline, covering system architecture, mathematical formulations, blocking algorithms, gradient-boosted matching models, streaming inference, and official validation protocols.

---

## Technical Documentation Navigation

### 1. Getting Started & Setup
* [**Getting Started (`getting-started.md`)](getting-started.md)**: 5-minute onboarding guide to install, test, and run the pipeline.
* [**Installation Guide (`installation.md`)](installation.md)**: Detailed dependency requirements, virtual environment isolation, and platform notes (macOS, Linux, Windows).
* [**Configuration (`configuration.md`)](configuration.md)**: CLI argument reference, hyperparameter defaults, and directory layouts.

### 2. Architecture & Contracts
* [**Project Architecture (`project-architecture.md`)](project-architecture.md)**: High-level and component architecture, data flow, memory boundaries, and streaming design.
* [**Data Dictionary (`data-dictionary.md`)](data-dictionary.md)**: Field-by-field definitions, types, nullability, and noise profiles for Source 1, 2, 3, and Ground Truth.
* [**Data Contract (`data-contract.md`)](data-contract.md)**: Strict schemas, TSV tab delimiter guarantees, ID prefix constraints, and subset invariants.
* [**Methodology (`methodology.md`)](methodology.md)**: Problem analysis, entity resolution theory, and algorithmic pipeline stages.

### 3. Pipeline Stages
* [**Candidate Generation (`candidate-generation.md`)](candidate-generation.md)**: Multi-rule inverted index blocking, core tokens, character n-grams, and search space reduction.
* [**Matching Model (`matching-model.md`)](matching-model.md)**: `HistGradientBoostingClassifier`, 20-dimensional pairwise features, missing-value handling, and threshold calibration.
* [**Training Workflow (`training.md`)](training.md)**: Negative sampling strategies, validation split generation, and hyperparameter tuning.
* [**Streaming Inference (`inference.md`)](inference.md)**: Batched, memory-bounded prediction across 1.73M test records with frozen candidate snapshots.

### 4. Evaluation & Validation
* [**Evaluation & Metrics (`evaluation.md`)](evaluation.md)**: Formal mathematical definition of Macro $F_{0.5}$, singleton handling, and reduction ratios.
* [**Submission Validation (`validation.md`)](validation.md)**: Official challenge validator execution, checklist, and verification logs.
* [**Experiments & Ablations (`experiments.md`)](experiments.md)**: Empirical benchmarks, blocking rule contributions, and threshold sweep results.
* [**Reproducibility Guide (`reproducibility.md`)](reproducibility.md)**: Deterministic reproduction instructions, random seeds, and environment isolation.

### 5. Engineering Standards & Operations
* [**Testing Guide (`testing.md`)](testing.md)**: Automated pytest suite (32 unit and integration tests) and coverage inventory.
* [**Troubleshooting (`troubleshooting.md`)](troubleshooting.md)**: Common failure modes, memory spikes, delimiter errors, and diagnostics.
* [**System Limitations (`limitations.md`)](limitations.md)**: Edge cases, severe abbreviation failure modes, and scalability boundaries.
* [**Privacy & Data Handling (`privacy-and-data-handling.md`)](privacy-and-data-handling.md)**: Air-gapped compute, zero external telemetry, and data security.
* [**Model Card (`model-card.md`)](model-card.md)**: Standard ML model card covering training data, performance bounds, and intended use.
* [**Dataset Card (`dataset-card.md`)](dataset-card.md)**: Dataset overview, source heterogeneity, country shifts, and schema quirks.

### 6. Architecture Decisions & Governance
* [**Architecture Decision Records (`decisions/`)](decisions/README.md)**: Index of formal Architecture Decision Records (ADRs).
* [**ADR-0001: System & Architecture Decisions (`decisions/ADR-0001-documentation-and-architecture-decisions.md`)](decisions/ADR-0001-documentation-and-architecture-decisions.md)**: Record of core architectural choices (pure Python metrics, HistGradientBoosting, candidate snapshot invariant).
* [**Codebase Audit (`REPOSITORY_AUDIT.md`)](REPOSITORY_AUDIT.md)**: Comprehensive reconnaissance report on repo status and completed features.
* [**License Selection (`LICENSE_SELECTION.md`)](LICENSE_SELECTION.md)**: Detailed comparison and selection guidance between Apache 2.0 and MIT.
