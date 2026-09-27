.PHONY: help install test train predict validate clean lint

PYTHON ?= python3
PYTHONPATH := code/business_entity_resolution:$(PYTHONPATH)
export PYTHONPATH

help:
	@echo "Amazon Business Entity Resolution — Developer Commands"
	@echo "======================================================="
	@echo "  make install    Install Python dependencies"
	@echo "  make test       Run the automated pytest suite (32 tests)"
	@echo "  make train      Train HistGradientBoosting model & tune threshold"
	@echo "  make predict    Run streaming inference on test set & generate TSVs"
	@echo "  make validate   Run official submission validator on output files"
	@echo "  make clean      Remove temporary cache and bytecode files"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest tests/ -v

train:
	$(PYTHON) -m src.pipeline \
	  --mode train \
	  --train-s1 student_resource/dataset/train/train_source1.tsv \
	  --train-s2 student_resource/dataset/train/train_source2.tsv \
	  --train-s3 student_resource/dataset/train/train_source3.tsv \
	  --ground-truth student_resource/dataset/train/train_ground_truth.tsv \
	  --model-path output/model.pkl

predict:
	$(PYTHON) -m src.pipeline \
	  --mode predict \
	  --test-s1 student_resource/dataset/test/test_source1.tsv \
	  --test-s2 student_resource/dataset/test/test_source2.tsv \
	  --test-s3 student_resource/dataset/test/test_source3.tsv \
	  --model-path output/model.pkl \
	  --output-dir output

validate:
	$(PYTHON) student_resource/utils/validate_submission.py \
	  --matching output/matching_results.tsv \
	  --candidate output/candidate_pairs.tsv \
	  --test-dir student_resource/dataset/test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
