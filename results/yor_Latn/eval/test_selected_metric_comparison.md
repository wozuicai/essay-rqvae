# yor_Latn Test Metric Comparison

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average | 7914 | 0.211523881729 | 1674 | 0.233131159970 | 1845 | 0.233257518322 | 1846 |
| original_variant_v0 | 1319 | 0.168309325246 | 222 | 0.194086429113 | 256 | 0.194086429113 | 256 |
| sid_rules_selected | 1319 | 0.310083396513 | 409 | 0.334344200152 | 441 | 0.334344200152 | 441 |
| lgbm_all_levels_selected | 1319 | 0.300227445034 | 396 | 0.327520849128 | 432 | 0.327520849128 | 432 |
| lgbm_exclude_level0_selected | 1319 | 0.297952994693 | 393 | 0.325246398787 | 429 | 0.325246398787 | 429 |

Detail files:
- `/root/gsm8k_single_language_experiment/yor_Latn/analysis/test_selection_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/yor_Latn/analysis_lgbm/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/yor_Latn/analysis_lgbm_no_level0/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/yor_Latn/eval/test_selected_metric_summary.json`
