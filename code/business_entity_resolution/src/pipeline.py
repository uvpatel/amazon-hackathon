"""End-to-end business entity resolution pipeline execution script."""

import argparse
import os
import pandas as pd
from .utils import load_dataset, save_tsv
from .blocking import run_blocking
from .matching import score_and_match


def run_pipeline(
    data_dir: str,
    output_dir: str,
    threshold: float = 0.80,
) -> None:
    """Execute end-to-end pipeline: data -> blocking -> matching -> output."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading data from {data_dir}...")
    source1_path = os.path.join(data_dir, "source_1.tsv")
    source2_path = os.path.join(data_dir, "source_2.tsv")
    source3_path = os.path.join(data_dir, "source_3.tsv")

    if not os.path.exists(source1_path):
        print(f"Dataset files not found in {data_dir}. Generating sample outputs...")
        source1_df = pd.DataFrame([{"entity_id": "s1_001", "name": "Example Corp"}])
        pool_df = pd.DataFrame([
            {"entity_id": "s2_001", "name": "Example Corporation"},
            {"entity_id": "s3_001", "name": "Other LLC"},
        ])
    else:
        source1_df = load_dataset(source1_path)
        source2_df = load_dataset(source2_path) if os.path.exists(source2_path) else pd.DataFrame()
        source3_df = load_dataset(source3_path) if os.path.exists(source3_path) else pd.DataFrame()
        pool_df = pd.concat([source2_df, source3_df], ignore_index=True)

    # 1. Blocking / Candidate Generation
    print("Running candidate generation (blocking)...")
    candidate_pairs_df = run_blocking(
        source1_df=source1_df,
        candidates_pool_df=pool_df,
    )
    candidates_output_path = os.path.join(output_dir, "candidate_pairs.tsv")
    save_tsv(candidate_pairs_df, candidates_output_path)
    print(f"Saved candidate pairs to {candidates_output_path}")

    # 2. Matching / Scoring
    print("Running matching and classification...")
    source1_lookup = source1_df.set_index("entity_id").to_dict(orient="index")
    pool_lookup = pool_df.set_index("entity_id").to_dict(orient="index")

    matching_results_df = score_and_match(
        candidate_pairs_df=candidate_pairs_df,
        source1_lookup=source1_lookup,
        pool_lookup=pool_lookup,
        threshold=threshold,
    )
    matching_output_path = os.path.join(output_dir, "matching_results.tsv")
    save_tsv(matching_results_df, matching_output_path)
    print(f"Saved final matching results to {matching_output_path}")
    print("Pipeline execution completed successfully.")


def main():
    parser = argparse.ArgumentParser(description="Run Business Entity Resolution Pipeline")
    parser.add_argument("--data_dir", type=str, default="./data", help="Directory containing input dataset files")
    parser.add_argument("--output_dir", type=str, default="../../output", help="Directory to save final output files")
    parser.add_argument("--threshold", type=float, default=0.80, help="Matching similarity threshold")
    args = parser.parse_args()

    run_pipeline(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        threshold=args.threshold,
    )


if __name__ == "__main__":
    main()
