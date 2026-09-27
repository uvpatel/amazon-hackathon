"""Tests for data loading, schema validation, and submission file generation."""

import os
import tempfile
import pytest
import pandas as pd
from src.utils import (
    load_tsv,
    parse_ground_truth,
    write_submission_file,
    ValidationError,
    SOURCE_REQUIRED_COLUMNS,
    GROUND_TRUTH_COLUMNS,
)


def test_load_tsv_valid():
    content = "entity_id\tbusiness_name\tbusiness_address\tcountry\nS1-0001\tTest Corp\t123 Main St\tUS\n"
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tmp:
        tmp.write(content)
        tmp.flush()
        filepath = tmp.name

    try:
        df = load_tsv(filepath, expected_columns=SOURCE_REQUIRED_COLUMNS, expected_prefix="S1-")
        assert len(df) == 1
        assert df.iloc[0]["entity_id"] == "S1-0001"
        assert df.iloc[0]["business_name"] == "Test Corp"
        assert df.iloc[0]["country"] == "US"
    finally:
        os.remove(filepath)


def test_load_tsv_missing_columns():
    content = "entity_id\tbusiness_name\nS1-0001\tTest Corp\n"
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tmp:
        tmp.write(content)
        tmp.flush()
        filepath = tmp.name

    try:
        with pytest.raises(ValidationError, match="Missing required columns"):
            load_tsv(filepath, expected_columns=SOURCE_REQUIRED_COLUMNS)
    finally:
        os.remove(filepath)


def test_load_tsv_invalid_prefix():
    content = "entity_id\tbusiness_name\tbusiness_address\tcountry\nS2-0001\tTest Corp\t123 Main St\tUS\n"
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tmp:
        tmp.write(content)
        tmp.flush()
        filepath = tmp.name

    try:
        with pytest.raises(ValidationError, match="must start with 'S1-'"):
            load_tsv(filepath, expected_columns=SOURCE_REQUIRED_COLUMNS, expected_prefix="S1-")
    finally:
        os.remove(filepath)


def test_load_tsv_duplicate_id():
    content = (
        "entity_id\tbusiness_name\tbusiness_address\tcountry\n"
        "S1-0001\tTest Corp\t123 Main St\tUS\n"
        "S1-0001\tTest Corp 2\t456 Elm St\tUS\n"
    )
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tmp:
        tmp.write(content)
        tmp.flush()
        filepath = tmp.name

    try:
        with pytest.raises(ValidationError, match="Duplicate entity_id detected"):
            load_tsv(filepath, expected_columns=SOURCE_REQUIRED_COLUMNS)
    finally:
        os.remove(filepath)


def test_parse_ground_truth_valid():
    content = (
        "source1_entity_id\tmatched_entity_ids\n"
        "S1-0001\tS2-00047,S3-00812\n"
        "S1-0002\t\n"
        "S1-0003\tS2-00099\n"
    )
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tmp:
        tmp.write(content)
        tmp.flush()
        filepath = tmp.name

    try:
        gt = parse_ground_truth(filepath)
        assert len(gt) == 3
        assert gt["S1-0001"] == {"S2-00047", "S3-00812"}
        assert gt["S1-0002"] == set()
        assert gt["S1-0003"] == {"S2-00099"}
    finally:
        os.remove(filepath)


def test_parse_ground_truth_reject_self_match():
    content = (
        "source1_entity_id\tmatched_entity_ids\n"
        "S1-0001\tS1-0002\n"
    )
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tmp:
        tmp.write(content)
        tmp.flush()
        filepath = tmp.name

    try:
        with pytest.raises(ValidationError, match="S1 self-matches"):
            parse_ground_truth(filepath)
    finally:
        os.remove(filepath)


def test_write_submission_file():
    s1_ids = ["S1-0001", "S1-0002", "S1-0003"]
    mapping = {
        "S1-0001": ["S2-100", "S3-200", "S2-100"],  # dupe should be removed
        "S1-0002": set(),  # singleton
        "S1-0003": ["S3-300"],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "matching_results.tsv")
        write_submission_file(s1_ids, mapping, out_path, "matched_entity_ids")

        with open(out_path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\r\n") for line in f]

        assert lines[0] == "source1_entity_id\tmatched_entity_ids"
        assert lines[1] == "S1-0001\tS2-100,S3-200"
        assert lines[2] == "S1-0002\t"
        assert lines[3] == "S1-0003\tS3-300"
