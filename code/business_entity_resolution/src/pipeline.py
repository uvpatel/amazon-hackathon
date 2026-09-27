"""End-to-end training, validation, and batched streaming inference pipeline for Business Entity Resolution."""

import argparse
import os
import sys
import time
from typing import Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from .blocking import BlockingIndex, retrieve_candidates_for_s1, run_blocking_pipeline
from .features import build_pair_feature_matrix
from .metrics import compute_blocking_metrics, compute_macro_f05
from .model import EntityMatchingModel
from .normalization import (
    get_core_name_tokens,
    normalize_address,
    normalize_country,
    normalize_name,
)
from .utils import (
    GROUND_TRUTH_COLUMNS,
    SOURCE_REQUIRED_COLUMNS,
    load_tsv,
    parse_ground_truth,
    write_submission_file,
    write_tsv,
)


def extract_targeted_pool_subset(
    source2_path: str,
    source3_path: str,
    needed_entity_ids: Set[str],
    bg_sample_per_source: int = 25000,
) -> pd.DataFrame:
    """Stream through S2 and S3 to collect all ground-truth targets plus background negatives."""
    records = []
    for path in [source2_path, source3_path]:
        bg_count = 0
        with open(path, "r", encoding="utf-8") as f:
            header_line = next(f)
            headers = [h.strip() for h in header_line.rstrip("\r\n").split("\t")]
            for line in f:
                parts = line.rstrip("\r\n").split("\t")
                if len(parts) >= len(headers):
                    eid = parts[0]
                    if eid in needed_entity_ids or bg_count < bg_sample_per_source:
                        row_dict = dict(zip(headers, parts))
                        records.append(row_dict)
                        if eid not in needed_entity_ids:
                            bg_count += 1

    return pd.DataFrame(records)


def load_targeted_ground_truth(gt_path: str, needed_s1_ids: Set[str]) -> Dict[str, Set[str]]:
    """Stream ground truth and extract exact match sets for specified S1 IDs."""
    gt_map: Dict[str, Set[str]] = {}
    with open(gt_path, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\r\n").split("\t")
            if not parts:
                continue
            s1_id = parts[0].strip()
            if s1_id in needed_s1_ids:
                raw_matches = parts[1].strip() if len(parts) > 1 else ""
                matched_set = set([m.strip() for m in raw_matches.split(",") if m.strip()])
                gt_map[s1_id] = matched_set
                if len(gt_map) == len(needed_s1_ids):
                    break
    for s1_id in needed_s1_ids:
        if s1_id not in gt_map:
            gt_map[s1_id] = set()
    return gt_map


def train_and_validate(
    train_s1_path: str,
    train_s2_path: str,
    train_s3_path: str,
    ground_truth_path: str,
    model_save_path: str,
    train_sample_size: int = 3000,
    val_sample_size: int = 1000,
    max_candidates_per_s1: int = 15,
    random_seed: int = 42,
) -> Dict[str, float]:
    """Train matching model and calibrate decision threshold on validation set."""
    print("=== Phase: Training and Validation ===")
    total_samples = train_sample_size + val_sample_size
    print(f"Loading {total_samples} S1 records from {train_s1_path}...")

    s1_df = load_tsv(train_s1_path, expected_columns=SOURCE_REQUIRED_COLUMNS, expected_prefix="S1-", nrows=total_samples)
    s1_ids_set = set(s1_df["entity_id"])
    print(f"Extracting ground truth for {len(s1_ids_set)} entities from {ground_truth_path}...")
    gt = load_targeted_ground_truth(ground_truth_path, s1_ids_set)

    rng = np.random.RandomState(random_seed)
    shuffled_idx = rng.permutation(len(s1_df))
    train_idx = shuffled_idx[:train_sample_size]
    val_idx = shuffled_idx[train_sample_size:]

    train_s1 = s1_df.iloc[train_idx].copy().reset_index(drop=True)
    val_s1 = s1_df.iloc[val_idx].copy().reset_index(drop=True)
    print(f"Train S1 entities: {len(train_s1)}, Validation S1 entities: {len(val_s1)}")

    needed_targets = set()
    for eid in s1_df["entity_id"]:
        needed_targets.update(gt.get(eid, set()))
    print(f"Collecting candidate target pool ({len(needed_targets)} true targets + background records)...")

    pool_df = extract_targeted_pool_subset(
        source2_path=train_s2_path,
        source3_path=train_s3_path,
        needed_entity_ids=needed_targets,
        bg_sample_per_source=25000,
    )
    print(f"Constructed training pool of {len(pool_df)} records.")

    # 1. Blocking on Training Split
    print("Running blocking on training set...")
    train_cand_map, train_prov, index = run_blocking_pipeline(
        source1_df=train_s1,
        pool_df=pool_df,
        max_candidates_per_s1=max_candidates_per_s1,
    )

    train_pairs: List[Tuple[str, str]] = []
    train_labels: List[int] = []

    s1_norm_lookup = {}
    for _, row in train_s1.iterrows():
        eid = str(row["entity_id"]).strip()
        s1_norm_lookup[eid] = {
            "norm_name": normalize_name(str(row.get("business_name", ""))),
            "norm_addr": normalize_address(str(row.get("business_address", ""))),
            "norm_country": normalize_country(str(row.get("country", ""))),
        }
        true_matches = gt.get(eid, set())
        candidates = train_cand_map.get(eid, [])

        for cid in candidates:
            train_pairs.append((eid, cid))
            train_labels.append(1 if cid in true_matches else 0)

        for t_mid in true_matches:
            if t_mid in index.pool_records and t_mid not in candidates:
                train_pairs.append((eid, t_mid))
                train_labels.append(1)

    print(f"Training pairs: {len(train_pairs)} ({sum(train_labels)} positives, {len(train_labels) - sum(train_labels)} negatives).")

    X_train = build_pair_feature_matrix(
        candidate_pairs=train_pairs,
        s1_records=s1_norm_lookup,
        pool_records=index.pool_records,
        provenance_map=train_prov,
    )
    y_train = np.array(train_labels, dtype=np.int32)

    print("Fitting EntityMatchingModel...")
    model = EntityMatchingModel(random_state=random_seed)
    model.fit(X_train, y_train)

    # 2. Validation & Threshold Calibration
    print("Running blocking on validation set...")
    val_cand_map, val_prov, _ = run_blocking_pipeline(
        source1_df=val_s1,
        pool_df=pool_df,
        max_candidates_per_s1=max_candidates_per_s1,
    )

    val_gt = {eid: gt[eid] for eid in val_s1["entity_id"]}
    blocking_metrics = compute_blocking_metrics(val_cand_map, val_gt, total_possible_targets=len(pool_df))
    print(f"Validation Blocking Recall: {blocking_metrics['blocking_recall']:.4f}")
    print(f"Validation Reduction Ratio: {blocking_metrics['reduction_ratio']:.6f}")
    print(f"Validation Avg Candidates per S1: {blocking_metrics['avg_candidates_per_s1']:.2f}")

    val_pairs: List[Tuple[str, str]] = []
    val_s1_norm_lookup = {}
    for _, row in val_s1.iterrows():
        eid = str(row["entity_id"]).strip()
        val_s1_norm_lookup[eid] = {
            "norm_name": normalize_name(str(row.get("business_name", ""))),
            "norm_addr": normalize_address(str(row.get("business_address", ""))),
            "norm_country": normalize_country(str(row.get("country", ""))),
        }
        for cid in val_cand_map.get(eid, []):
            val_pairs.append((eid, cid))

    print(f"Scoring {len(val_pairs)} validation pairs...")
    X_val = build_pair_feature_matrix(
        candidate_pairs=val_pairs,
        s1_records=val_s1_norm_lookup,
        pool_records=index.pool_records,
        provenance_map=val_prov,
    )
    val_probs = model.predict_proba(X_val)
    val_prob_map = {pair: float(prob) for pair, prob in zip(val_pairs, val_probs)}

    best_thresh, best_f05 = model.calibrate_threshold(
        candidate_map=val_cand_map,
        pair_probabilities=val_prob_map,
        ground_truth=val_gt,
    )
    print(f"Optimal Decision Threshold: {best_thresh:.2f} (Validation Macro F0.5: {best_f05:.4f})")

    model.save(model_save_path)
    print(f"Model saved to {model_save_path}")

    return {
        "best_threshold": float(best_thresh),
        "validation_macro_f05": float(best_f05),
        "blocking_recall": float(blocking_metrics["blocking_recall"]),
        "reduction_ratio": float(blocking_metrics["reduction_ratio"]),
        "avg_candidates_per_s1": float(blocking_metrics["avg_candidates_per_s1"]),
    }


def build_streaming_pool_index(
    source2_path: str,
    source3_path: str,
    sample_limit: Optional[int] = None,
) -> BlockingIndex:
    """Build fast inverted index over Source 2 and Source 3 files."""
    t0 = time.time()
    print("Building target candidate pool index from Source 2 and Source 3...")
    index = BlockingIndex(max_token_freq=1000)

    for path in [source2_path, source3_path]:
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            header_line = next(f)
            headers = [h.strip() for h in header_line.rstrip("\r\n").split("\t")]
            name_idx = headers.index("business_name") if "business_name" in headers else 1
            addr_idx = headers.index("business_address") if "business_address" in headers else 2
            country_idx = headers.index("country") if "country" in headers else 3

            for line in f:
                parts = line.rstrip("\r\n").split("\t")
                if len(parts) >= len(headers):
                    eid = parts[0]
                    raw_name = parts[name_idx]
                    raw_addr = parts[addr_idx]
                    raw_country = parts[country_idx]

                    norm_name = normalize_name(raw_name)
                    norm_addr = normalize_address(raw_addr)
                    norm_country = normalize_country(raw_country)

                    index.pool_records[eid] = (norm_name, norm_addr, norm_country)

                    if norm_name:
                        index.exact_name_index[norm_name].add(eid)
                        for token in get_core_name_tokens(norm_name):
                            if len(token) >= 3:
                                index.core_token_index[token].add(eid)
                    if norm_name and len(norm_name) >= 4:
                        index.prefix_index[norm_name[:4]].add(eid)

                count += 1
                if sample_limit and count >= sample_limit:
                    break

        print(f"  Processed {count} records from {os.path.basename(path)}")

    index.core_token_index = {
        t: eids for t, eids in index.core_token_index.items()
        if len(eids) <= index.max_token_freq
    }
    index.prefix_index = {
        p: eids for p, eids in index.prefix_index.items()
        if len(eids) <= index.max_token_freq
    }
    print(f"Candidate index ready: {len(index.pool_records)} total entities in {time.time() - t0:.2f}s")
    return index


def flush_inference_batch(
    batch_entities: List[Tuple[str, List[str]]],
    batch_pairs: List[Tuple[str, str]],
    batch_s1_dict: Dict[str, Tuple[str, str, str]],
    batch_prov: Dict[Tuple[str, str], Set[str]],
    index: BlockingIndex,
    model: EntityMatchingModel,
    cand_f,
    match_f,
) -> None:
    """Score a batch of candidate pairs using model and write results immediately to output files."""
    prob_map: Dict[Tuple[str, str], float] = {}
    if batch_pairs:
        X = build_pair_feature_matrix(batch_pairs, batch_s1_dict, index.pool_records, batch_prov)
        probs = model.predict_proba(X)
        for pair, prob in zip(batch_pairs, probs):
            prob_map[pair] = float(prob)

    for s1_id, candidates in batch_entities:
        cand_str = ",".join(candidates)
        cand_f.write(f"{s1_id}\t{cand_str}\n")

        if candidates:
            accepted = [cid for cid in candidates if prob_map.get((s1_id, cid), 0.0) >= model.threshold]
            match_str = ",".join(accepted)
            match_f.write(f"{s1_id}\t{match_str}\n")
        else:
            match_f.write(f"{s1_id}\t\n")


def run_inference(
    test_s1_path: str,
    test_s2_path: str,
    test_s3_path: str,
    model_path: str,
    output_dir: str,
    max_candidates_per_s1: int = 15,
    sample_limit: Optional[int] = None,
    batch_size: int = 10000,
) -> Tuple[str, str]:
    """Run batched streaming inference on test set to generate matching_results.tsv and candidate_pairs.tsv."""
    t0 = time.time()
    os.makedirs(output_dir, exist_ok=True)
    candidate_output_path = os.path.join(output_dir, "candidate_pairs.tsv")
    matching_output_path = os.path.join(output_dir, "matching_results.tsv")

    if os.path.isfile(model_path):
        print(f"Loading model from {model_path}...")
        model = EntityMatchingModel.load(model_path)
    else:
        print("Model file not found; initializing default model...")
        model = EntityMatchingModel()
        model.threshold = 0.65

    print(f"Inference decision threshold: {model.threshold:.2f}")

    # Build target index
    index = build_streaming_pool_index(test_s2_path, test_s3_path, sample_limit=sample_limit)

    print(f"Streaming through Test Source 1 ({test_s1_path}) with batch size {batch_size}...")
    cand_f = open(candidate_output_path, "w", encoding="utf-8", newline="\n")
    match_f = open(matching_output_path, "w", encoding="utf-8", newline="\n")

    cand_f.write("source1_entity_id\tcandidate_entity_ids\n")
    match_f.write("source1_entity_id\tmatched_entity_ids\n")

    processed = 0
    batch_entities: List[Tuple[str, List[str]]] = []
    batch_pairs: List[Tuple[str, str]] = []
    batch_s1_dict: Dict[str, Tuple[str, str, str]] = {}
    batch_prov: Dict[Tuple[str, str], Set[str]] = {}

    with open(test_s1_path, "r", encoding="utf-8") as f:
        header_line = next(f)
        headers = [h.strip() for h in header_line.rstrip("\r\n").split("\t")]
        name_idx = headers.index("business_name") if "business_name" in headers else 1
        addr_idx = headers.index("business_address") if "business_address" in headers else 2
        country_idx = headers.index("country") if "country" in headers else 3

        for line in f:
            parts = line.rstrip("\r\n").split("\t")
            if not parts or not parts[0]:
                continue

            s1_id = parts[0]
            raw_name = parts[name_idx] if len(parts) > name_idx else ""
            raw_addr = parts[addr_idx] if len(parts) > addr_idx else ""
            raw_country = parts[country_idx] if len(parts) > country_idx else ""

            norm_name = normalize_name(raw_name)
            norm_addr = normalize_address(raw_addr)
            norm_country = normalize_country(raw_country)

            s1_dict = {
                "entity_id": s1_id,
                "business_name": raw_name,
                "business_address": raw_addr,
                "country": raw_country,
                "norm_name": norm_name,
                "norm_addr": norm_addr,
                "norm_country": norm_country,
            }

            candidates, prov = retrieve_candidates_for_s1(
                s1_row=s1_dict,
                index=index,
                max_candidates_per_s1=max_candidates_per_s1,
            )

            batch_entities.append((s1_id, candidates))
            batch_s1_dict[s1_id] = (norm_name, norm_addr, norm_country)
            for cid in candidates:
                batch_pairs.append((s1_id, cid))
                batch_prov[(s1_id, cid)] = prov.get(cid, set())

            processed += 1

            if len(batch_entities) >= batch_size:
                flush_inference_batch(
                    batch_entities, batch_pairs, batch_s1_dict, batch_prov,
                    index, model, cand_f, match_f
                )
                batch_entities = []
                batch_pairs = []
                batch_s1_dict = {}
                batch_prov = {}

                if processed % 100000 == 0:
                    print(f"  Processed {processed:,} test entities in {time.time() - t0:.1f}s...")

            if sample_limit and processed >= sample_limit:
                break

    # Flush remaining
    if batch_entities:
        flush_inference_batch(
            batch_entities, batch_pairs, batch_s1_dict, batch_prov,
            index, model, cand_f, match_f
        )

    cand_f.close()
    match_f.close()
    print(f"Generated {processed:,} output rows in {time.time() - t0:.2f} seconds.")
    return matching_output_path, candidate_output_path


def main():
    parser = argparse.ArgumentParser(description="Amazon Business Entity Resolution Pipeline")
    parser.add_argument("--mode", choices=["train", "predict", "all"], default="all")
    parser.add_argument("--train-s1", default="student_resource/dataset/train/train_source1.tsv")
    parser.add_argument("--train-s2", default="student_resource/dataset/train/train_source2.tsv")
    parser.add_argument("--train-s3", default="student_resource/dataset/train/train_source3.tsv")
    parser.add_argument("--ground-truth", default="student_resource/dataset/train/train_ground_truth.tsv")
    parser.add_argument("--test-s1", default="student_resource/dataset/test/test_source1.tsv")
    parser.add_argument("--test-s2", default="student_resource/dataset/test/test_source2.tsv")
    parser.add_argument("--test-s3", default="student_resource/dataset/test/test_source3.tsv")
    parser.add_argument("--model-path", default="output/model.pkl")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--sample-limit", type=int, default=None)

    args = parser.parse_args()

    if args.mode in ("train", "all"):
        train_and_validate(
            train_s1_path=args.train_s1,
            train_s2_path=args.train_s2,
            train_s3_path=args.train_s3,
            ground_truth_path=args.ground_truth,
            model_save_path=args.model_path,
            train_sample_size=3000,
            val_sample_size=1000,
        )

    if args.mode in ("predict", "all"):
        run_inference(
            test_s1_path=args.test_s1,
            test_s2_path=args.test_s2,
            test_s3_path=args.test_s3,
            model_path=args.model_path,
            output_dir=args.output_dir,
            sample_limit=args.sample_limit,
        )


if __name__ == "__main__":
    main()
