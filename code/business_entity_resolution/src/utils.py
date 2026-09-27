"""Utility functions for preprocessing, text normalization, and I/O."""

import re
import unicodedata
import pandas as pd
from typing import List, Optional


def normalize_text(text: Optional[str]) -> str:
    """Normalize string by lowercasing, stripping punctuation and redundant whitespace."""
    if not isinstance(text, str) or pd.isna(text):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_dataset(filepath: str, sep: str = "\t") -> pd.DataFrame:
    """Load dataset from TSV or CSV."""
    return pd.read_csv(filepath, sep=sep, dtype=str)


def save_tsv(df: pd.DataFrame, filepath: str) -> None:
    """Save dataframe as a tab-separated file."""
    df.to_csv(filepath, sep="\t", index=False)
