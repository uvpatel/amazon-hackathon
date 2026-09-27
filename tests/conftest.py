"""Pytest configuration and pythonpath setup."""

import os
import sys

# Add code/business_entity_resolution to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "code", "business_entity_resolution")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
