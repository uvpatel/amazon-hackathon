"""Unit tests for pairwise feature extraction."""

import numpy as np
import pytest
from src.features import (
    FEATURE_NAMES,
    extract_pair_features,
    build_pair_feature_matrix,
    token_jaccard,
    token_sort_similarity,
)


def test_token_jaccard():
    t1 = ["prime", "money", "corp"]
    t2 = ["prime", "money", "llc"]
    assert pytest.approx(token_jaccard(t1, t2)) == 2.0 / 4.0
    assert token_jaccard([], t2) == 0.0


def test_token_sort_similarity():
    s1 = "corp prime money"
    s2 = "money prime corp"
    assert token_sort_similarity(s1, s2) == 1.0


def test_extract_pair_features_exact():
    s1 = {
        "norm_name": "acme supply company",
        "norm_addr": "100 industrial park road",
        "norm_country": "US",
    }
    s2 = {
        "norm_name": "acme supply company",
        "norm_addr": "100 industrial park road",
        "norm_country": "US",
    }
    feats = extract_pair_features(s1, s2, provenance_rules={"exact_name"})
    assert len(feats) == len(FEATURE_NAMES)
    # Check exact flags
    idx_name_exact = FEATURE_NAMES.index("name_exact_match")
    idx_addr_exact = FEATURE_NAMES.index("addr_exact_match")
    idx_country = FEATURE_NAMES.index("country_match")
    assert feats[idx_name_exact] == 1.0
    assert feats[idx_addr_exact] == 1.0
    assert feats[idx_country] == 1.0


def test_extract_pair_features_missing_fields_no_nan():
    s1 = {"norm_name": "solo store", "norm_addr": "", "norm_country": "FRANCE"}
    s2 = {"norm_name": "", "norm_addr": "12 rue de la paix", "norm_country": "FRANCE"}

    feats = extract_pair_features(s1, s2, provenance_rules=set())
    assert len(feats) == len(FEATURE_NAMES)
    assert not any(np.isnan(f) for f in feats)
    assert not any(np.isinf(f) for f in feats)

    idx_s1_empty = FEATURE_NAMES.index("s1_addr_empty")
    idx_target_empty = FEATURE_NAMES.index("target_name_empty")
    assert feats[idx_s1_empty] == 1.0
    assert feats[idx_target_empty] == 1.0


def test_build_pair_feature_matrix():
    pairs = [("S1-1", "S2-1"), ("S1-1", "S3-1")]
    s1_lookup = {"S1-1": {"norm_name": "abc", "norm_addr": "123 st", "norm_country": "US"}}
    pool_lookup = {
        "S2-1": {"norm_name": "abc", "norm_addr": "123 st", "norm_country": "US"},
        "S3-1": {"norm_name": "xyz", "norm_addr": "456 rd", "norm_country": "US"},
    }
    prov = {("S1-1", "S2-1"): {"rule1"}, ("S1-1", "S3-1"): {"rule2"}}

    mat = build_pair_feature_matrix(pairs, s1_lookup, pool_lookup, prov)
    assert mat.shape == (2, len(FEATURE_NAMES))
    assert not np.isnan(mat).any()
