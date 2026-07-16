# Essay RQ-VAE GSM8K Low-Resource Experiments

This repository contains the lightweight, reproducible parts of a GSM8K
low-resource rewrite and SID-selection experiment.

The current checked-in experiment is for `swh_Latn` (Swahili). Large generated
artifacts are intentionally excluded from Git.

## Contents

- `scripts/`
  - `run_gsm8k_single_language_experiment.py`: main pipeline entrypoint.
  - `rqvae_title_pipeline.py`: RQ-VAE model utilities used by the SID stage.
  - `train_lgbm_sid_selector.py`: optional LightGBM SID selector.
  - `translate_gsm8k_nllb_direct.py`: NLLB translation helper.
  - `launch_swh_eval.sh`: example 8-GPU eval launcher.
- `docs/`
  - reusable workflow documentation and run notes.
- `results/swh_Latn/`
  - lightweight metadata, audit summaries, metric summaries, CSV rule exports,
    selection CSVs, and RQ-VAE training metrics.

## Excluded Artifacts

The full run produced large or environment-specific artifacts that are not
checked in:

- model weights such as `model.pt`
- hidden-state and SID memmaps
- generated parquet datasets
- full rewrite/evaluation JSONL outputs
- vLLM/NLLB caches and logs
- local SSH/deploy keys

The checked-in result files are enough to inspect the run configuration,
selection results, SID rule tables, LightGBM comparison, and audit summaries.
To rerun the full pipeline, use the workflow in
`docs/reusable_gsm8k_low_resource_sid_pipeline.md` and stage the required
models/datasets locally.
