# Installation & Environment Setup

This document provides detailed setup instructions for the **Amazon Business Entity Resolution** system across multiple operating systems, including virtual environment configuration and dependency management.

---

## 1. System Requirements

### Hardware
- **CPU**: Modern x86-64 or ARM64 processor (e.g. Intel Core i5/i7/i9, AMD Ryzen, Apple Silicon M1/M2/M3/M4).
- **RAM**: Minimum 8 GB. 16 GB+ recommended for running high-throughput streaming inference across 10 million test records without swapping.
- **Disk Space**: At least 5 GB free disk space for raw TSV datasets, intermediate indices, and submission output TSVs.

### Software
- **Python**: Version 3.9, 3.10, 3.11, 3.12, or 3.14.
- **C/C++ Compiler**: Not required. The pipeline uses pure Python string metrics and standard scikit-learn wheel distributions, requiring zero native compilation steps.

---

## 2. Dependency Specification

The pipeline dependencies are pinned in `requirements.txt`:

| Package | Minimum Version | Purpose |
| :--- | :--- | :--- |
| `pandas` | `>= 2.0.0` | Tabular data structures, chunked reading, and TSV I/O |
| `numpy` | `>= 1.24.0` | Vectorized numerical arrays and matrix operations |
| `scikit-learn` | `>= 1.3.0` | `HistGradientBoostingClassifier` and evaluation utilities |
| `scipy` | `>= 1.11.0` | Scientific computing support for scikit-learn |
| `pytest` | `>= 8.0.0` | Automated test suite execution |

---

## 3. Platform-Specific Setup

### A. macOS (Apple Silicon / Intel)

1. Ensure Python 3 is installed (via Homebrew or official installer):
   ```bash
   brew install python@3.11  # or use existing system Python 3
   ```
2. Navigate to the project root:
   ```bash
   cd amazon-hackathon
   ```
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

*Note on OpenMP on macOS:*
Earlier iterations tested LightGBM and XGBoost, which failed on macOS due to missing `libomp.dylib`. Our pipeline uses Scikit-Learn's `HistGradientBoostingClassifier`, which operates without external OpenMP libraries, guaranteeing out-of-the-box execution on macOS without `brew install libomp`.

---

### B. Linux (Ubuntu / Debian / CentOS / RHEL)

1. Install Python 3, `pip`, and `venv`:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-pip python3-venv
   ```
2. Set up virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### C. Windows (PowerShell or WSL)

We strongly recommend **WSL (Windows Subsystem for Linux)** for large-scale TSV processing. However, native PowerShell is supported:

1. In PowerShell:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 4. Verifying Environment Health

Run the following command to verify that all packages are installed correctly:

```bash
python3 -c "
import pandas as pd
import numpy as np
import sklearn
import scipy
import pytest

print('Environment Check Passed:')
print(f'  pandas:       {pd.__version__}')
print(f'  numpy:        {np.__version__}')
print(f'  scikit-learn: {sklearn.__version__}')
print(f'  scipy:        {scipy.__version__}')
print(f'  pytest:       {pytest.__version__}')
"
```

Then execute the test suite:
```bash
python3 -m pytest tests/ -v
```
All 32 tests must pass.
