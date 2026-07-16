# GSM8K swh_Latn Task Status Summary

Last updated: 2026-07-15 12:07:51 UTC

## Current State

The refreshed swh_Latn pipeline is complete. No GPU or LightGBM job is currently running.

The completed work so far is for one language: `swh_Latn` (Swahili).

## Completed

### Data Preparation

- Source language dataset prepared under:
  `/root/gsm8k_single_language_experiment/swh_Latn`
- Source rows:
  - Train: `7473`
  - Test: `1319`
  - Total: `8792`

### English Query Rewrites

- Used `/mnt/bn/search-gec-agentic-search-useast1b/guo/gpt-oss-120B` through vLLM.
- Ran 8-GPU data parallel rewrite.
- Final valid English rewrite coverage: `8792 / 8792`.
- Each source question has 5 English rewrites.
- Some difficult records needed repeated gpt-oss/NLLB passes; final fallback/template records were removed from the final rewrite file.

### Swahili Rewrites

- Translated English rewrites with `/root/nllb-200-1.3B`.
- Final Swahili rewrite records:
  - Records: `8792`
  - Valid: `8792`
  - Bad: `0`
  - Missing: `0`
- All previous fallback/template records have been replaced.
- Current final rewrite models:
  - `8557` records: `gpt-oss-120B + nllb-200-1.3B`
  - `235` records: `true_manual_swahili_rewrite_by_agent`
- Remaining `manual_structural_swahili_rewrite_by_agent` records: `0`
- Chinese contamination: `0`
- Final file:
  `/root/gsm8k_single_language_experiment/swh_Latn/rewrites/rewrite_records.jsonl`

### Variant Table

- Built original question + 5 rewrites.
- Output:
  `/root/gsm8k_single_language_experiment/swh_Latn/variants/variants.parquet`
- Shape: `52752 x 8`
- Counts:
  - Train: `44838`
  - Test: `7914`
  - Each source has variants `0..5`.

### Qwen Hidden States

- Model: `/root/qwen3.5-9B-instruct`
- Confirmed hidden output shape is embedding layer + 32 layers:
  `33 x 4096`
- Final hidden-state memmap:
  `/root/gsm8k_single_language_experiment/swh_Latn/hidden/hidden_states.float16.memmap`
- Shape: `[52752, 33, 4096]`
- Dtype: `float16`
- Missing rows: `0`

### RQ-VAE

- Trained one configuration, no parameter sweep:
  - `latent_dim=256`
  - `num_codebooks=3`
  - `codebook_size=256`
  - `beta_commit=0.25`
  - normalized embeddings
- Training embeddings: `1479654`
- Final validation MSE: `4.6805269569934656e-05`
- Model:
  `/root/gsm8k_single_language_experiment/swh_Latn/rqvae/model.pt`

### SID Encoding

- SID memmap:
  `/root/gsm8k_single_language_experiment/swh_Latn/rqvae/sids.uint16.memmap`
- Shape: `[52752, 33, 3]`
- Metrics:
  `/root/gsm8k_single_language_experiment/swh_Latn/rqvae/sid_metrics.json`
- Caveat: codebook utilization is poor at level 0, so later SID-rule analysis should treat that level carefully.

### LightGBM SID Selector

- Script:
  `/root/train_lgbm_sid_selector.py`
- Final runs used `--num-boost-round 200 --num-threads 16`.
- All SID levels:
  `/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/analysis_lgbm_summary.json`
- Excluding collapsed level0:
  `/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/analysis_lgbm_summary.json`
- Comparison note:
  `/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_comparison.md`

### Eval Metrics

- Current `prediction` / `correct` columns are strict-format GSM8K metrics.
- Strict parser accepts only explicit final-answer markers: `####`, `\boxed{}`,
  `answer is`, or `final answer is`.
- Additional relaxed columns have been added to:
  `/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_results.parquet`
- Metric note:
  `/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_metric_comparison.md`

## Paused / Not Final
None for this one-language refreshed run.

## Final Results

- Eval rows: `52752`
- Eval missing rows: `0`
- Strict-format accuracy: `0.48650288140734`
- Strict train accuracy: `0.48846960167714887`
- Strict test accuracy: `0.47536012130401817`
- Strict prediction missing: `13842 / 52752` (`0.26239763421292084`)
- Relaxed last-number accuracy: `0.5141226872914771`
- Relaxed train accuracy: `0.5159462955528793`
- Relaxed test accuracy: `0.5037907505686126`
- Strict-else-relaxed accuracy: `0.513971034273582`
- Strict-else-relaxed test accuracy: `0.5036643922163255`
- Strict parse failures recovered by relaxed last-number: `1449`
- Test original accuracy: `0.4981046247156937`
- Test selected accuracy by SID rules: `0.5526914329037149`
- Test selected accuracy by LightGBM, all SID levels: `0.5534495830174374`
- Test selected accuracy by LightGBM, exclude level0: `0.5519332827899924`
- Significant SID rules: `895`
- Script audit: `/root/gsm8k_single_language_experiment/swh_Latn/audit_report.json`, `ok=true`, refreshed `2026-07-15 12:09:47 UTC`

On the `1319` test questions, the original variant got `657` correct, SID-rule
selection got `729` correct, all-level LightGBM got `730` correct, and no-level0
LightGBM got `728` correct.

## Detailed Log

Detailed step-by-step notes are in:
`/root/gsm8k_query_rewrite_rqvae_worklog.md`
