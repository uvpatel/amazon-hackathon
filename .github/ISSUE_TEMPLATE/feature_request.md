---
name: Feature Request
about: Suggest an idea or enhancement for the entity resolution pipeline
title: '[ENHANCEMENT] <concise description>'
labels: ['enhancement']
assignees: ''
---

## Feature Summary
A clear and concise description of the proposed feature or improvement.

## Motivation & Use Case
Why is this feature needed? What limitation or challenge requirement does it address?
(e.g., higher blocking recall, faster streaming throughput, support for novel transliteration).

## Proposed Solution / Technical Approach
Describe how this feature should be implemented, including affected modules:
- [ ] `src/utils.py`
- [ ] `src/normalization.py`
- [ ] `src/blocking.py`
- [ ] `src/features.py`
- [ ] `src/model.py`
- [ ] `src/pipeline.py`

## Alternatives Considered
A clear description of any alternative solutions or workarounds you have considered.

## Impact on Invariants & Constraints
- Does this change require external dependencies? (Must satisfy open-source compliance & zero internet calls)
- Does this impact the candidate-match subset invariant?
- Estimated impact on Macro F0.5 or runtime performance:
