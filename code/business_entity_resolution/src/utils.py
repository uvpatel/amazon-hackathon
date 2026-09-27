"""Data loading, schema validation, and TSV I/O utilities."""

import os
from typing import Dict, List, Optional, Set, Union
import pandas as pd

SOURCE_REQUIRED_COLUMNS = ["entity_id", "business_name", "business_address", "country"]
GROUND_TRUTH_COLUMNS = ["source1_entity_id", "matched_entity_ids"]
MATCHING_HEADER = ["source1_entity_id", "matched_entity_ids"]
CANDIDATE_HEADER = ["source1_entity_id", "candidate_entity_ids"]


class ValidationError(Exception):
    """Raised when data contracts or schema invariants are violated."""
    pass


def load_tsv(
    filepath: str,
    expected_columns: Optional[List[str]] = None,
    expected_prefix: Optional[str] = None,
    check_unique_ids: bool = True,
    nrows: Optional[int] = None,
) -> pd.DataFrame:
    """Load a TSV file with strict string typing and contract validation.

    Args:
        filepath: Path to the TSV file.
        expected_columns: List of columns required to be in the TSV.
        expected_prefix: If specified, validates entity_id column starts with this prefix.
        check_unique_ids: If True, asserts entity_id has no duplicates.
        nrows: Optional row limit for sampling.

    Returns:
        pd.DataFrame with all columns as strings and empty values preserved as "".
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"TSV file not found: {filepath}")

    df = pd.read_csv(
        filepath,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        nrows=nrows,
    )

    if expected_columns is not None:
        missing_cols = [c for c in expected_columns if c not in df.columns]
        if missing_cols:
            raise ValidationError(
                f"Missing required columns {missing_cols} in {filepath}. Found: {list(df.columns)}"
            )

    if "entity_id" in df.columns:
        if expected_prefix:
            invalid_ids = df[~df["entity_id"].str.startswith(expected_prefix)]["entity_id"].tolist()
            if invalid_ids:
                sample = invalid_ids[:5]
                raise ValidationError(
                    f"Entity IDs in {filepath} must start with '{expected_prefix}'. Found invalid IDs: {sample}"
                )

        if check_unique_ids:
            dup_ids = df[df.duplicated(subset=["entity_id"], keep=False)]["entity_id"].unique().tolist()
            if dup_ids:
                raise ValidationError(
                    f"Duplicate entity_id detected in {filepath}: {dup_ids[:5]}"
                )

    return df


def parse_ground_truth(filepath: str, nrows: Optional[int] = None) -> Dict[str, Set[str]]:
    """Parse train_ground_truth.tsv into a mapping of source1_entity_id to set of matched IDs.

    Args:
        filepath: Path to train_ground_truth.tsv
        nrows: Optional limit for testing/debugging.

    Returns:
        Dict mapping S1 ID to set of matched S2/S3 IDs.
    """
    df = load_tsv(filepath, expected_columns=GROUND_TRUTH_COLUMNS, check_unique_ids=True, nrows=nrows)

    ground_truth: Dict[str, Set[str]] = {}
    for _, row in df.iterrows():
        s1_id = str(row["source1_entity_id"]).strip()
        raw_matches = str(row["matched_entity_ids"]).strip()
        if not raw_matches:
            ground_truth[s1_id] = set()
            continue

        matched_list = [m.strip() for m in raw_matches.split(",") if m.strip()]
        for mid in matched_list:
            if mid.startswith("S1-"):
                raise ValidationError(f"Ground truth cannot contain S1 self-matches. Found {mid} for {s1_id}")
            if not mid.startswith(("S2-", "S3-")):
                raise ValidationError(f"Invalid match ID prefix (must be S2- or S3-): {mid} for {s1_id}")

        ground_truth[s1_id] = set(matched_list)

    return ground_truth


def write_submission_file(
    source1_ids: List[str],
    id_mapping: Dict[str, Union[List[str], Set[str]]],
    filepath: str,
    column_name: str,
) -> None:
    """Write an official tab-separated submission file (matching_results or candidate_pairs).

    Args:
        source1_ids: Complete ordered list of Source 1 entity IDs.
        id_mapping: Mapping from S1 ID to list/set of target IDs.
        filepath: Output TSV file destination.
        column_name: Either 'matched_entity_ids' or 'candidate_entity_ids'.
    """
    if column_name not in ("matched_entity_ids", "candidate_entity_ids"):
        raise ValueError(f"Invalid column_name: {column_name}")

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        # Write header with single tab
        f.write(f"source1_entity_id\t{column_name}\n")

        for s1_id in source1_ids:
            target_ids = id_mapping.get(s1_id, [])
            if isinstance(target_ids, set):
                target_ids = sorted(target_ids)
            else:
                # Deduplicate while preserving order
                seen = set()
                deduped = []
                for tid in target_ids:
                    if tid not in seen:
                        seen.add(tid)
                        deduped.append(tid)
                target_ids = deduped

            joined_targets = ",".join(target_ids)
            f.write(f"{s1_id}\t{joined_targets}\n")


def write_tsv(df: pd.DataFrame, filepath: str) -> None:
    """Save dataframe as tab-separated file."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    df.to_csv(filepath, sep="\t", index=False)

