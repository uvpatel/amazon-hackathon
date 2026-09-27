"""Unit tests for blocking and candidate generation."""

import pandas as pd
import pytest
from src.blocking import BlockingIndex, retrieve_candidates_for_s1, run_blocking_pipeline


def test_exact_name_blocking():
    pool_data = [
        {"entity_id": "S2-001", "business_name": "Acme Tools Inc", "business_address": "123 Main St", "country": "US"},
        {"entity_id": "S3-001", "business_name": "Unrelated LLC", "business_address": "456 Oak Rd", "country": "US"},
    ]
    pool_df = pd.DataFrame(pool_data)

    index = BlockingIndex()
    index.build_from_dataframe(pool_df)

    s1_row = {"entity_id": "S1-001", "business_name": "Acme Tools, Inc.", "business_address": "123 Main Street", "country": "US"}
    candidates, prov = retrieve_candidates_for_s1(s1_row, index, max_candidates_per_s1=10)

    assert "S2-001" in candidates
    assert "exact_name" in prov["S2-001"]


def test_core_token_fuzzy_blocking():
    pool_data = [
        {"entity_id": "S2-002", "business_name": "Red Perfect Trading Corp", "business_address": "Awas Vikas", "country": "India"},
    ]
    pool_df = pd.DataFrame(pool_data)
    index = BlockingIndex()
    index.build_from_dataframe(pool_df)

    s1_row = {"entity_id": "S1-002", "business_name": "Red Perfect Enterprises", "business_address": "Mirzapur", "country": "India"}
    candidates, prov = retrieve_candidates_for_s1(s1_row, index, max_candidates_per_s1=10)

    assert "S2-002" in candidates
    assert any("token_" in r for r in prov["S2-002"])


def test_no_s1_self_matches_or_duplicates():
    pool_data = [
        {"entity_id": "S2-001", "business_name": "Tech Corp", "business_address": "101 Alpha Rd", "country": "US"},
        {"entity_id": "S3-001", "business_name": "Tech Corp", "business_address": "101 Alpha Rd", "country": "US"},
    ]
    pool_df = pd.DataFrame(pool_data)

    s1_data = [
        {"entity_id": "S1-001", "business_name": "Tech Corp", "business_address": "101 Alpha Rd", "country": "US"},
        {"entity_id": "S1-002", "business_name": "Completely Unique Store", "business_address": "999 Nowhere", "country": "US"},
    ]
    s1_df = pd.DataFrame(s1_data)

    cand_map, prov_map, _ = run_blocking_pipeline(s1_df, pool_df, max_candidates_per_s1=5)

    # Invariants
    for s1_id, cands in cand_map.items():
        # No duplicates
        assert len(cands) == len(set(cands))
        # No S1 self matches
        for cid in cands:
            assert not cid.startswith("S1-")
            assert cid.startswith(("S2-", "S3-"))

    # S1-001 matched S2-001 and S3-001
    assert "S2-001" in cand_map["S1-001"]
    assert "S3-001" in cand_map["S1-001"]

    # S1-002 has empty candidates
    assert cand_map["S1-002"] == []
