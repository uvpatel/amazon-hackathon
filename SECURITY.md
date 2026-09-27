# Security Policy

## 1. Supported Versions

This project is maintained for the **Amazon ML Challenge 2026**. Security updates and bug fixes are applied exclusively to the latest active commit on the `main` branch.

| Version / Branch | Supported | Notes |
|---|---|---|
| `main` | :white_check_mark: Yes | Active challenge development |
| Prior tags / commits | :x: No | Historical reference only |

---

## 2. Reporting a Vulnerability

We take the security and integrity of this project seriously. If you discover a security vulnerability or sensitive data exposure, please disclose it responsibly.

### How to Report
- **Preferred Method:** Use **GitHub Private Vulnerability Reporting** via the repository's `Security` tab (if enabled by the maintainer).
- **Alternative Contact:** If GitHub Private Reporting is unavailable, contact the repository maintainers directly via their verified GitHub profiles.
- **Maintainer Notice:** A dedicated private security email has not yet been designated. *Do NOT open public GitHub issues for security vulnerabilities, API keys, or private data exposures.*

### Response Timeline
- **Initial Acknowledgment:** Within 48 business hours (estimated; maintainer-configured).
- **Status Updates & Remediation:** Timeline depends on severity and complexity; patches will be committed to `main`.

---

## 3. Scope of Security Considerations

This project processes tabular data (TSV) and executes machine learning inference. Security considerations include:

1. **Serialized Model Artifacts (`.pkl`):** The repository saves and loads scikit-learn models using Python's standard `pickle` serialization. **Never load untrusted `.pkl` files** from unverified sources, as unpickling arbitrary data can lead to remote code execution.
2. **Dataset & File Handling:** All file parsers enforce explicit tab separation (`sep="\t"`) and strict string typing (`dtype=str`) to prevent formula injection, buffer overruns, or type coercion vulnerabilities.
3. **Data Privacy & Fair Play:** In compliance with the Amazon ML Challenge rules, this repository strictly avoids external network lookups, third-party APIs, or web scraping. Real challenge datasets and ground truth labels must never be checked into public repositories.
4. **Dependency Hygiene:** Dependencies (`pandas`, `numpy`, `scikit-learn`, `scipy`, `pytest`) are pinned to verified, stable versions to prevent supply-chain vulnerabilities.

---

## 4. Responsible Disclosure

When reporting an issue, please include:
- A description of the vulnerability and its potential impact.
- Step-by-step instructions or a minimal reproducible proof-of-concept.
- Any affected code modules or file paths.

We request that you give the maintainers reasonable time to investigate and remediate the issue prior to public disclosure.
