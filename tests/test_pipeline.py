"""Integration tests for end-to-end training and inference pipeline."""

import os
import subprocess
import sys
import tempfile
import pandas as pd
import pytest

from src.pipeline import train_and_validate, run_inference
from src.utils import write_tsv


def test_end_to_end_pipeline_and_official_validator():
    """Verify entire pipeline on synthetic data and validate with official validate_submission.py."""
    with tempfile.TemporaryDirectory() as tmpdir:
        train_dir = os.path.join(tmpdir, "train")
        test_dir = os.path.join(tmpdir, "test")
        out_dir = os.path.join(tmpdir, "output")
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)
        os.makedirs(out_dir, exist_ok=True)

        # Synthetic train records
        train_s1 = pd.DataFrame([
            {"entity_id": "S1-100", "business_name": "Alpha Tech Corp", "business_address": "100 Innovation Way, Austin, TX", "country": "US"},
            {"entity_id": "S1-200", "business_name": "Beta Pharma LLC", "business_address": "200 Health Blvd, Boston, MA", "country": "US"},
            {"entity_id": "S1-300", "business_name": "Gamma Supermarket", "business_address": "300 Market St, Mumbai", "country": "India"},
            {"entity_id": "S1-400", "business_name": "Delta Bistro", "business_address": "400 Food St, Paris", "country": "France"},
        ])
        train_s2 = pd.DataFrame([
            {"entity_id": "S2-101", "business_name": "Alpha Tech Inc", "business_address": "100 Innovation Way", "country": "US"},
            {"entity_id": "S2-301", "business_name": "Gamma Market", "business_address": "300 Market Street", "country": "India"},
        ])
        train_s3 = pd.DataFrame([
            {"entity_id": "S3-102", "business_name": "Alpha Technologies", "business_address": "100 Innovation Way, Austin", "country": "US"},
            {"entity_id": "S3-202", "business_name": "Beta Pharmaceuticals", "business_address": "200 Health Boulevard", "country": "US"},
        ])
        train_gt = pd.DataFrame([
            {"source1_entity_id": "S1-100", "matched_entity_ids": "S2-101,S3-102"},
            {"source1_entity_id": "S1-200", "matched_entity_ids": "S3-202"},
            {"source1_entity_id": "S1-300", "matched_entity_ids": "S2-301"},
            {"source1_entity_id": "S1-400", "matched_entity_ids": ""},  # singleton
        ])

        s1_path = os.path.join(train_dir, "train_source1.tsv")
        s2_path = os.path.join(train_dir, "train_source2.tsv")
        s3_path = os.path.join(train_dir, "train_source3.tsv")
        gt_path = os.path.join(train_dir, "train_ground_truth.tsv")

        train_s1.to_csv(s1_path, sep="\t", index=False)
        train_s2.to_csv(s2_path, sep="\t", index=False)
        train_s3.to_csv(s3_path, sep="\t", index=False)
        train_gt.to_csv(gt_path, sep="\t", index=False)

        model_path = os.path.join(out_dir, "model.pkl")

        # 1. Train and validate
        report = train_and_validate(
            train_s1_path=s1_path,
            train_s2_path=s2_path,
            train_s3_path=s3_path,
            ground_truth_path=gt_path,
            model_save_path=model_path,
            train_sample_size=3,
            val_sample_size=1,
            max_candidates_per_s1=5,
        )
        assert os.path.isfile(model_path)
        assert "validation_macro_f05" in report

        # 2. Test inference
        test_s1 = pd.DataFrame([
            {"entity_id": "S1-901", "business_name": "Alpha Tech", "business_address": "100 Innovation Way", "country": "US"},
            {"entity_id": "S1-902", "business_name": "Unknown Entity Nowhere", "business_address": "999 Ghost Road", "country": "France"},
        ])
        test_s2 = pd.DataFrame([
            {"entity_id": "S2-901", "business_name": "Alpha Tech Solutions", "business_address": "100 Innovation Way, Austin", "country": "US"},
        ])
        test_s3 = pd.DataFrame([
            {"entity_id": "S3-901", "business_name": "Alpha Tech Corp", "business_address": "100 Innovation Way", "country": "US"},
        ])

        test_s1_path = os.path.join(test_dir, "test_source1.tsv")
        test_s2_path = os.path.join(test_dir, "test_source2.tsv")
        test_s3_path = os.path.join(test_dir, "test_source3.tsv")

        test_s1.to_csv(test_s1_path, sep="\t", index=False)
        test_s2.to_csv(test_s2_path, sep="\t", index=False)
        test_s3.to_csv(test_s3_path, sep="\t", index=False)

        match_file, cand_file = run_inference(
            test_s1_path=test_s1_path,
            test_s2_path=test_s2_path,
            test_s3_path=test_s3_path,
            model_path=model_path,
            output_dir=out_dir,
            max_candidates_per_s1=5,
        )

        assert os.path.isfile(match_file)
        assert os.path.isfile(cand_file)

        # 3. Execute official validator
        validator_script = os.path.abspath("student_resource/utils/validate_submission.py")
        cmd = [
            sys.executable,
            validator_script,
            "--matching", match_file,
            "--candidate", cand_file,
            "--test-dir", test_dir,
            "--check-ids",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"Validator failed: {res.stdout}\n{res.stderr}"
        assert "PASS — no blocking issues found. Safe to submit." in res.stdout
