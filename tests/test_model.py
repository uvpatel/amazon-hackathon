"""Unit tests for EntityMatchingModel, threshold tuning, and multi-match prediction."""

import os
import tempfile
import numpy as np
import pytest
from src.model import EntityMatchingModel


def test_fit_and_predict_proba():
    # 20 samples, 20 features
    X = np.random.RandomState(42).randn(40, 20).astype(np.float32)
    y = np.array([1] * 20 + [0] * 20)

    model = EntityMatchingModel(random_state=42, max_iter=20)
    model.fit(X, y)
    assert model.is_fitted

    probs = model.predict_proba(X)
    assert len(probs) == 40
    assert (probs >= 0.0).all()
    assert (probs <= 1.0).all()


def test_predict_matches_subset_invariant():
    model = EntityMatchingModel()
    candidate_map = {
        "S1-1": ["S2-10", "S2-20", "S3-30"],
        "S1-2": ["S2-40"],
        "S1-3": [],  # singleton candidate
    }
    pair_probs = {
        ("S1-1", "S2-10"): 0.85,
        ("S1-1", "S2-20"): 0.30,
        ("S1-1", "S3-30"): 0.90,
        ("S1-2", "S2-40"): 0.45,
    }

    # Threshold 0.80
    matches = model.predict_matches(candidate_map, pair_probs, threshold=0.80)

    # Invariants
    for s1_id, matched_list in matches.items():
        cand_set = set(candidate_map[s1_id])
        # Subset invariant
        for m in matched_list:
            assert m in cand_set

    # S1-1 has S3-30 (0.90) and S2-10 (0.85) in descending order
    assert matches["S1-1"] == ["S3-30", "S2-10"]
    # S1-2 has no candidates above 0.80 -> empty
    assert matches["S1-2"] == []
    # S1-3 has no candidates -> empty
    assert matches["S1-3"] == []


def test_calibrate_threshold():
    model = EntityMatchingModel()
    candidate_map = {
        "S1-1": ["S2-10", "S2-20"],
        "S1-2": ["S2-30"],
    }
    pair_probs = {
        ("S1-1", "S2-10"): 0.85,  # True match
        ("S1-1", "S2-20"): 0.40,  # False positive
        ("S1-2", "S2-30"): 0.35,  # True match is empty (S1-2 is singleton)
    }
    ground_truth = {
        "S1-1": {"S2-10"},
        "S1-2": set(),
    }

    best_thresh, best_score = model.calibrate_threshold(
        candidate_map,
        pair_probs,
        ground_truth,
        thresholds=[0.30, 0.50, 0.80],
    )
    # Threshold >= 0.50 correctly rejects S2-20 and S2-30, achieving F0.5 = 1.0!
    assert best_thresh >= 0.50
    assert pytest.approx(best_score) == 1.0


def test_save_and_load_model():
    X = np.random.RandomState(42).randn(20, 20).astype(np.float32)
    y = np.array([1] * 10 + [0] * 10)
    model = EntityMatchingModel(random_state=42, max_iter=10)
    model.fit(X, y)
    model.threshold = 0.72

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "model.pkl")
        model.save(path)

        loaded = EntityMatchingModel.load(path)
        assert loaded.is_fitted
        assert loaded.threshold == 0.72

        p1 = model.predict_proba(X)
        p2 = loaded.predict_proba(X)
        np.testing.assert_allclose(p1, p2)
