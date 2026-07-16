# swh_Latn SID Selection: Rule Baseline vs LightGBM

Last updated: 2026-07-15 10:41:00 UTC

## Inputs

- Variant table: `/root/gsm8k_single_language_experiment/swh_Latn/variants/variants.parquet`
- Eval results: `/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_results.parquet`
- SID memmap: `/root/gsm8k_single_language_experiment/swh_Latn/rqvae/sids.uint16.memmap`
- SID shape: `[52752, 33, 3]`
- Test source questions: `1319`
- Test variant rows: `7914`

Each LightGBM example is one variant. Features are categorical SID ids from
all `(layer, codebook_level)` positions. The label is whether Qwen3.5 answered
that variant correctly in the aligned GSM8K `####` eval.

## Commands

Initial 600-round jobs were started for both all-level and no-level0 settings,
but running both concurrently with the original `num_threads=-1` setting was too
slow and produced no output after roughly 12 minutes. Those two jobs were stopped.

The script was then updated to support `--num-threads`, and the final runs used
200 boosting rounds with 16 CPU threads:

```bash
/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python \
  /root/train_lgbm_sid_selector.py \
  --out-dir /root/gsm8k_single_language_experiment/swh_Latn \
  --num-boost-round 200 \
  --num-threads 16
```

```bash
/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python \
  /root/train_lgbm_sid_selector.py \
  --out-dir /root/gsm8k_single_language_experiment/swh_Latn \
  --num-boost-round 200 \
  --num-threads 16 \
  --exclude-level0
```

## Results

| Selector | Features | Test selected accuracy | Correct / 1319 | Delta vs original | Delta vs SID rules |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original variant only | none | `0.4981046247156937` | `657` | `0` | `-0.0545868081880212` |
| SID rules | significant SID buckets | `0.5526914329037149` | `729` | `+72` | `0` |
| LightGBM, all levels | `99` SID features | `0.5534495830174374` | `730` | `+73` | `+1` |
| LightGBM, exclude level0 | `66` SID features | `0.5519332827899924` | `728` | `+71` | `-1` |

Variant-level metrics:

```text
all-level LGBM:
  train_auc = 0.9469978031321118
  test_auc = 0.7092131767937975
  test_variant_accuracy_at_0_5 = 0.6549153399039677

no-level0 LGBM:
  train_auc = 0.9470908309670145
  test_auc = 0.7105024358789189
  test_variant_accuracy_at_0_5 = 0.653904473085671
```

## Interpretation

LightGBM is at least competitive with the hand-scored SID-rule selector on this
one-language run. The all-level model selected one more correct test question
than the SID-rule selector: `730` correct vs `729` correct.

Removing level0 did not improve final per-question selection even though level0
has severe codebook collapse in the RQ-VAE metrics. The no-level0 model had a
slightly higher variant-level AUC, but its final selected-question accuracy was
one question lower than the rule selector and two questions lower than the
all-level LightGBM model.

The practical conclusion is that collapsed level0 should still be treated
cautiously for human rule interpretation, but excluding it is not clearly better
for LightGBM selection in this run.

## Output Files

All-level LightGBM:

```text
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/analysis_lgbm_summary.json
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/test_variant_scores.parquet
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/test_variant_scores.csv
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/test_selection_lgbm.parquet
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/test_selection_lgbm.csv
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/feature_importance.csv
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/model.txt
```

No-level0 LightGBM:

```text
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/analysis_lgbm_summary.json
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/test_variant_scores.parquet
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/test_variant_scores.csv
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/test_selection_lgbm.parquet
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/test_selection_lgbm.csv
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/feature_importance.csv
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/model.txt
```

