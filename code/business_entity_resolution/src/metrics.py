"""Official metric calculation: Macro-averaged F0.5 per Source 1 entity."""

from typing import Dict, List, Set
import numpy as np


def compute_entity_f05(predicted: Set[str], truth: Set[str]) -> float:
    """Compute F0.5 score for a single Source 1 entity.

    Formula:
        F0.5 = (1.25 * Precision * Recall) / (0.25 * Precision + Recall)

    Singleton semantics:
        - Truth is empty, Predicted is empty => 1.0
        - Truth is empty, Predicted non-empty => 0.0
        - Truth is non-empty, Predicted is empty => 0.0
    """
    if not truth:
        # Singleton entity
        return 1.0 if not predicted else 0.0

    if not predicted:
        # Missed match for non-singleton
        return 0.0

    tp = len(predicted & truth)
    if tp == 0:
        return 0.0

    precision = tp / len(predicted)
    recall = tp / len(truth)

    denom = 0.25 * precision + recall
    if denom == 0:
        return 0.0

    return (1.25 * precision * recall) / denom


def compute_macro_f05(
    predictions: Dict[str, Set[str]],
    ground_truth: Dict[str, Set[str]],
) -> Dict[str, float]:
    """Compute macro-averaged F0.5 score across all Source 1 entities in ground truth.

    Args:
        predictions: Dict mapping source1_entity_id -> set of predicted match IDs.
        ground_truth: Dict mapping source1_entity_id -> set of true match IDs.

    Returns:
        Dict containing:
            - 'macro_f05': Macro-averaged F0.5
            - 'precision': Average precision on entities with predictions
            - 'recall': Average recall across non-singleton entities
            - 'singleton_f05': Mean score for true singletons
            - 'non_singleton_f05': Mean score for non-singletons
            - 'num_entities': Total S1 entities evaluated
    """
    scores: List[float] = []
    singleton_scores: List[float] = []
    non_singleton_scores: List[float] = []
    precisions: List[float] = []
    recalls: List[float] = []

    for s1_id, truth in ground_truth.items():
        pred = predictions.get(s1_id, set())
        f05 = compute_entity_f05(pred, truth)
        scores.append(f05)

        if not truth:
            singleton_scores.append(f05)
        else:
            non_singleton_scores.append(f05)
            if pred:
                tp = len(pred & truth)
                precisions.append(tp / len(pred))
                recalls.append(tp / len(truth))
            else:
                recalls.append(0.0)

    return {
        "macro_f05": float(np.mean(scores)) if scores else 0.0,
        "precision": float(np.mean(precisions)) if precisions else 0.0,
        "recall": float(np.mean(recalls)) if recalls else 0.0,
        "singleton_f05": float(np.mean(singleton_scores)) if singleton_scores else 0.0,
        "non_singleton_f05": float(np.mean(non_singleton_scores)) if non_singleton_scores else 0.0,
        "num_entities": float(len(ground_truth)),
    }


def compute_blocking_metrics(
    candidate_map: Dict[str, Set[str]],
    ground_truth: Dict[str, Set[str]],
    total_possible_targets: int = 1,
) -> Dict[str, float]:
    """Compute candidate generation / blocking metrics.

    Args:
        candidate_map: Dict mapping S1 ID -> set of candidate IDs.
        ground_truth: Dict mapping S1 ID -> set of true matched IDs.
        total_possible_targets: Total number of records in S2 + S3.

    Returns:
        Dict with blocking recall, reduction ratio, average/median/P95 candidate counts.
    """
    total_true_pairs = 0
    recalled_true_pairs = 0
    candidate_counts: List[int] = []

    for s1_id, truth in ground_truth.items():
        candidates = candidate_map.get(s1_id, set())
        cand_set = set(candidates) if not isinstance(candidates, set) else candidates
        candidate_counts.append(len(cand_set))

        if truth:
            total_true_pairs += len(truth)
            recalled_true_pairs += len(truth & cand_set)

    total_candidates = sum(candidate_counts)
    num_s1 = max(1, len(ground_truth))
    total_possible_pairs = num_s1 * max(1, total_possible_targets)
    reduction_ratio = 1.0 - (total_candidates / total_possible_pairs)

    counts_arr = np.array(candidate_counts) if candidate_counts else np.array([0])

    return {
        "blocking_recall": float(recalled_true_pairs / total_true_pairs) if total_true_pairs > 0 else 1.0,
        "total_true_pairs": float(total_true_pairs),
        "recalled_true_pairs": float(recalled_true_pairs),
        "avg_candidates_per_s1": float(np.mean(counts_arr)),
        "median_candidates_per_s1": float(np.median(counts_arr)),
        "p95_candidates_per_s1": float(np.percentile(counts_arr, 95)),
        "total_candidate_pairs": float(total_candidates),
        "reduction_ratio": float(reduction_ratio),
    }
