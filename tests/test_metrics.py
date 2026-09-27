"""Unit tests for official Macro F0.5 metric and singleton scoring."""

import pytest
from src.metrics import compute_entity_f05, compute_macro_f05, compute_blocking_metrics


def test_official_worked_example():
    """Verify official example from hackathon problem statement:

    Predicted: [S2-00047, S2-00193, S3-00812]
    Ground truth: [S2-00047, S3-00812]
    Precision = 2/3, Recall = 1.0
    F0.5 = 0.7142857...
    """
    pred = {"S2-00047", "S2-00193", "S3-00812"}
    truth = {"S2-00047", "S3-00812"}

    score = compute_entity_f05(pred, truth)
    assert pytest.approx(score, rel=1e-3) == 0.714


def test_singleton_scoring():
    # 1. Truth empty, predicted empty => 1.0
    assert compute_entity_f05(set(), set()) == 1.0

    # 2. Truth empty, predicted non-empty => 0.0 (penalty for false merge on singleton)
    assert compute_entity_f05({"S2-00001"}, set()) == 0.0

    # 3. Truth non-empty, predicted empty => 0.0 (missed match)
    assert compute_entity_f05(set(), {"S2-00001"}) == 0.0


def test_perfect_match():
    pred = {"S2-1", "S3-2"}
    truth = {"S2-1", "S3-2"}
    assert compute_entity_f05(pred, truth) == 1.0


def test_macro_f05():
    ground_truth = {
        "S1-1": {"S2-1"},       # perfect match -> 1.0
        "S1-2": set(),          # perfect singleton -> 1.0
        "S1-3": set(),          # failed singleton -> 0.0
        "S1-4": {"S2-4"},       # missed match -> 0.0
    }
    predictions = {
        "S1-1": {"S2-1"},
        "S1-2": set(),
        "S1-3": {"S2-99"},
        "S1-4": set(),
    }

    result = compute_macro_f05(predictions, ground_truth)
    assert pytest.approx(result["macro_f05"]) == 0.50
    assert result["num_entities"] == 4.0
    assert pytest.approx(result["singleton_f05"]) == 0.50


def test_blocking_metrics():
    ground_truth = {
        "S1-1": {"S2-1", "S3-1"},
        "S1-2": {"S2-2"},
        "S1-3": set(),
    }
    candidate_map = {
        "S1-1": {"S2-1", "S2-99"},  # S2-1 captured, S3-1 missed
        "S1-2": {"S2-2"},           # S2-2 captured
        "S1-3": {"S2-88"},
    }
    # 3 true pairs in ground truth, 2 captured in candidates => 2/3 recall
    metrics = compute_blocking_metrics(candidate_map, ground_truth, total_possible_targets=100)
    assert pytest.approx(metrics["blocking_recall"]) == 2.0 / 3.0
    assert metrics["total_candidate_pairs"] == 4.0
    assert metrics["avg_candidates_per_s1"] == 4.0 / 3.0
    assert metrics["reduction_ratio"] > 0.95
