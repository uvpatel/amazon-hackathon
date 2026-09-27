"""Entity matching, similarity scoring, and classification."""

from typing import List, Dict, Optional
import pandas as pd
from rapidfuzz import fuzz
from .utils import normalize_text


def compute_string_similarity(str1: str, str2: str) -> float:
    """Compute token sort ratio similarity normalized to [0, 1]."""
    s1 = normalize_text(str1)
    s2 = normalize_text(str2)
    if not s1 or not s2:
        return 0.0
    return fuzz.token_sort_ratio(s1, s2) / 100.0


def score_and_match(
    candidate_pairs_df: pd.DataFrame,
    source1_lookup: Dict[str, Dict],
    pool_lookup: Dict[str, Dict],
    threshold: float = 0.80,
) -> pd.DataFrame:
    """Score candidate pairs and retain matches above threshold."""
    matching_results = []

    for _, row in candidate_pairs_df.iterrows():
        s1_id = str(row["source1_entity_id"])
        cand_str = str(row.get("candidate_entity_ids", ""))
        candidates = [c.strip() for c in cand_str.split(",") if c.strip()]

        s1_record = source1_lookup.get(s1_id, {})
        s1_name = s1_record.get("name", "")

        matched_ids = []
        for cand_id in candidates:
            cand_record = pool_lookup.get(cand_id, {})
            cand_name = cand_record.get("name", "")
            sim = compute_string_similarity(s1_name, cand_name)
            if sim >= threshold:
                matched_ids.append(cand_id)

        matching_results.append({
            "source1_entity_id": s1_id,
            "matched_entity_ids": ",".join(matched_ids),
        })

    return pd.DataFrame(matching_results)
