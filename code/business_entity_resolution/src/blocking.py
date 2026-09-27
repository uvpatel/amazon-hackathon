"""Candidate generation and blocking strategies for Business Entity Resolution."""

from typing import Dict, List, Set
import pandas as pd
from collections import defaultdict
from .utils import normalize_text


def generate_blocking_keys(name: str) -> List[str]:
    """Generate blocking keys from business entity names."""
    norm_name = normalize_text(name)
    tokens = norm_name.split()
    keys = []
    if tokens:
        # First word / prefix key
        keys.append(f"first_{tokens[0][:4]}")
        # 3-gram prefixes if token is long enough
        if len(tokens[0]) >= 3:
            keys.append(f"tri_{tokens[0][:3]}")
    return keys


def run_blocking(
    source1_df: pd.DataFrame,
    candidates_pool_df: pd.DataFrame,
    id_col_s1: str = "entity_id",
    name_col_s1: str = "name",
    id_col_pool: str = "entity_id",
    name_col_pool: str = "name",
    top_k: int = 20,
) -> pd.DataFrame:
    """Generate candidate pairs using inverted index blocking."""
    inverted_index: Dict[str, Set[str]] = defaultdict(set)

    for _, row in candidates_pool_df.iterrows():
        pool_id = str(row[id_col_pool])
        keys = generate_blocking_keys(str(row.get(name_col_pool, "")))
        for key in keys:
            inverted_index[key].add(pool_id)

    results = []
    for _, row in source1_df.iterrows():
        s1_id = str(row[id_col_s1])
        s1_keys = generate_blocking_keys(str(row.get(name_col_s1, "")))
        candidate_ids: Set[str] = set()
        for key in s1_keys:
            candidate_ids.update(inverted_index.get(key, set()))

        candidate_list = list(candidate_ids)[:top_k]
        results.append({
            "source1_entity_id": s1_id,
            "candidate_entity_ids": ",".join(candidate_list),
        })

    return pd.DataFrame(results)
