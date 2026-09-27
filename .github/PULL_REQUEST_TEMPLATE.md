## Description of Changes
A concise summary of what this pull request introduces or fixes. Reference any related issues (e.g. `Fixes #12`).

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking feature addition)
- [ ] Performance optimization (blocking reduction, vectorized features, memory optimization)
- [ ] Documentation update
- [ ] Test coverage addition

## Validation & Invariant Checklist
Before submitting this PR, verify the following strict project invariants:
- [ ] **Tests Pass**: `python3 -m pytest tests/ -v` passes with zero failures.
- [ ] **Challenge Invariant**: Output matches are guaranteed to be a subset of candidate pairs ($\text{matched} \subseteq \text{candidates}$).
- [ ] **TSV Formatting**: All I/O uses strict tab delimiters (`sep="\t"`) without comma artifacts.
- [ ] **Open-Set Geography**: No hardcoded countries or categorical one-hot vectors that break on France.
- [ ] **Dependencies**: No external API calls, geocoders, or non-permissive licensed models ($\le 8\text{B}$ parameters).
- [ ] **Code Hygiene**: Code formatted in adherence with `.editorconfig` (4-space indent, LF line endings).

## Verification Results
Attach pytest output or validation command result:
```text
Paste test output or validator log here
```
