"""Pairwise feature extraction for business entity resolution matching."""

import difflib
from typing import Dict, List, Set, Tuple
import numpy as np

FEATURE_NAMES = [
    "name_exact_match",
    "name_char_similarity",
    "name_token_jaccard",
    "name_token_sort_similarity",
    "name_core_token_overlap",
    "name_len_ratio",
    "addr_exact_match",
    "addr_char_similarity",
    "addr_token_jaccard",
    "addr_numeric_exact_match",
    "addr_numeric_overlap_count",
    "addr_len_ratio",
    "country_match",
    "s1_addr_empty",
    "target_addr_empty",
    "s1_name_empty",
    "target_name_empty",
    "combined_max_sim",
    "combined_product_sim",
    "provenance_rule_count",
]


def token_jaccard(tokens1: List[str], tokens2: List[str]) -> float:
    """Compute Jaccard similarity between two token lists."""
    if not tokens1 or not tokens2:
        return 0.0
    s1 = set(tokens1)
    s2 = set(tokens2)
    union = s1 | s2
    return len(s1 & s2) / len(union) if union else 0.0


def token_sort_similarity(text1: str, text2: str) -> float:
    """Sort tokens alphabetically and compute character similarity."""
    if not text1 or not text2:
        return 0.0
    sorted1 = " ".join(sorted(text1.split()))
    sorted2 = " ".join(sorted(text2.split()))
    return difflib.SequenceMatcher(None, sorted1, sorted2).ratio()


def extract_pair_features(
    s1_dict: Dict[str, str],
    target_dict: Dict[str, str],
    provenance_rules: Set[str],
) -> List[float]:
    """Compute feature vector for a single (Source 1, Target) candidate pair.

    Args:
        s1_dict: Normalized fields for Source 1 record.
        target_dict: Normalized fields for target record (from S2 or S3).
        provenance_rules: Set of blocking rules that produced this candidate pair.

    Returns:
        List of numeric features matching FEATURE_NAMES.
    """
    if isinstance(s1_dict, tuple):
        n1, a1, c1 = s1_dict
    else:
        n1 = s1_dict.get("norm_name", "")
        a1 = s1_dict.get("norm_addr", "")
        c1 = s1_dict.get("norm_country", "")

    if isinstance(target_dict, tuple):
        n2, a2, c2 = target_dict
    else:
        n2 = target_dict.get("norm_name", "")
        a2 = target_dict.get("norm_addr", "")
        c2 = target_dict.get("norm_country", "")

    # Name features
    name_exact = 1.0 if (n1 and n1 == n2) else 0.0
    name_char_sim = difflib.SequenceMatcher(None, n1, n2).ratio() if (n1 and n2) else 0.0
    t1 = n1.split()
    t2 = n2.split()
    name_jaccard = token_jaccard(t1, t2)
    name_sort_sim = token_sort_similarity(n1, n2)

    # Core token overlap
    c_t1 = set(t1)
    c_t2 = set(t2)
    core_overlap = float(len(c_t1 & c_t2))

    # Length ratio
    len1 = len(n1)
    len2 = len(n2)
    name_len_ratio = (min(len1, len2) / max(1, max(len1, len2))) if (len1 and len2) else 0.0

    # Address features
    addr_exact = 1.0 if (a1 and a1 == a2) else 0.0
    addr_char_sim = difflib.SequenceMatcher(None, a1, a2).ratio() if (a1 and a2) else 0.0
    at1 = a1.split()
    at2 = a2.split()
    addr_jaccard = token_jaccard(at1, at2)

    # Numeric address tokens
    nums1 = set([t for t in at1 if t.isdigit()])
    nums2 = set([t for t in at2 if t.isdigit()])
    numeric_exact = 1.0 if (nums1 and nums1 == nums2) else 0.0
    numeric_overlap = float(len(nums1 & nums2))

    addr_len1 = len(a1)
    addr_len2 = len(a2)
    addr_len_ratio = (min(addr_len1, addr_len2) / max(1, max(addr_len1, addr_len2))) if (addr_len1 and addr_len2) else 0.0

    # Country & missingness
    country_match = 1.0 if (c1 and c2 and c1 == c2) else 0.0
    s1_addr_empty = 1.0 if not a1 else 0.0
    target_addr_empty = 1.0 if not a2 else 0.0
    s1_name_empty = 1.0 if not n1 else 0.0
    target_name_empty = 1.0 if not n2 else 0.0

    # Interactions
    max_sim = max(name_char_sim, addr_char_sim)
    product_sim = name_char_sim * addr_char_sim

    rule_count = float(len(provenance_rules))

    return [
        name_exact,
        name_char_sim,
        name_jaccard,
        name_sort_sim,
        core_overlap,
        name_len_ratio,
        addr_exact,
        addr_char_sim,
        addr_jaccard,
        numeric_exact,
        numeric_overlap,
        addr_len_ratio,
        country_match,
        s1_addr_empty,
        target_addr_empty,
        s1_name_empty,
        target_name_empty,
        max_sim,
        product_sim,
        rule_count,
    ]


def build_pair_feature_matrix(
    candidate_pairs: List[Tuple[str, str]],
    s1_records: Dict[str, Dict[str, str]],
    pool_records: Dict[str, Dict[str, str]],
    provenance_map: Dict[Tuple[str, str], Set[str]],
) -> np.ndarray:
    """Build 2D numpy array of features for a list of candidate pairs.

    Args:
        candidate_pairs: List of (s1_id, candidate_id) pairs.
        s1_records: Lookup of S1 normalized records.
        pool_records: Lookup of pool normalized records.
        provenance_map: Lookup of (s1_id, cand_id) -> set of rules.

    Returns:
        np.ndarray of shape (len(candidate_pairs), len(FEATURE_NAMES)).
    """
    if not candidate_pairs:
        return np.empty((0, len(FEATURE_NAMES)), dtype=np.float32)

    rows = []
    for s1_id, cand_id in candidate_pairs:
        s1 = s1_records.get(s1_id, {})
        target = pool_records.get(cand_id, {})
        rules = provenance_map.get((s1_id, cand_id), set())
        feats = extract_pair_features(s1, target, rules)
        rows.append(feats)

    return np.array(rows, dtype=np.float32)
