# Privacy, Data Handling & Security Architecture

This document outlines the data governance, security posture, and privacy considerations implemented in the **Amazon Business Entity Resolution** system.

---

## 1. Threat Model & Air-Gapped Compute

### A. Zero Telemetry & Local Execution
- **Strict Isolation**: The pipeline operates completely offline. No telemetry, crash reporting, model weight downloading, or external API calls are made during any stage of training, validation, or inference.
- **Compliance with Challenge Rules**: The system conforms to the competition mandate prohibiting internet access, external geocoding, and web scraping.

### B. Serialized Model Safety
- **Risk**: Python's `pickle` serialization format can theoretically execute arbitrary code if untrusted model artifacts are loaded.
- **Mitigation**:
  - The model artifact (`output/model.pkl`) is generated strictly within the local pipeline.
  - Users are warned in [SECURITY.md](../SECURITY.md) never to load unverified third-party `.pkl` files.
  - Future iterations will evaluate migrating to secure serialization formats (such as ONNX or JSON-based tree structures).

---

## 2. Handling Commercial & Entity Data

### A. Nature of Records
The dataset consists exclusively of commercial business records:
- Business Legal / Trade Name
- Business Street Address
- Country of Operation
- Internal synthetic Entity Identifier

No Personally Identifiable Information (PII) such as personal Social Security Numbers, personal credit card numbers, or confidential financial transactions is processed by this system.

### B. Deterministic Sanitization
During normalization:
- Non-alphanumeric punctuation and control characters are stripped.
- Whitespace is collapsed into single spaces.
- Data is kept in memory only for the duration of the streaming batch and discarded immediately afterward.

---

## 3. Compliance & Governance Best Practices

- **GDPR / CCPA Considerations**: In enterprise deployment, entity resolution systems must support the "Right to be Forgotten" (GDPR Article 17). If an entity is deleted from Source 1, rebuilding the inverted index or filtering the reference list cleanly expunges all associated matches without requiring complete retraining of the gradient booster.
- **Model Explainability**: Because `HistGradientBoostingClassifier` operates on transparent, interpretable features (string similarities, token overlaps, numeric matches), match decisions can be inspected and justified with exact feature contribution values.
