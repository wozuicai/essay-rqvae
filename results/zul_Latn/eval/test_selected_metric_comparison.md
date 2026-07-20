# zul_Latn Test Metric Comparison

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average | 7914 | 0.289360626737 | 2290 | 0.313747788729 | 2483 | 0.313747788729 | 2483 |
| original_variant_v0 | 1319 | 0.266868840030 | 352 | 0.289613343442 | 382 | 0.289613343442 | 382 |
| sid_rules_selected | 1319 | 0.338134950720 | 446 | 0.364670204701 | 481 | 0.364670204701 | 481 |
| lgbm_all_levels_selected | 1319 | 0.353297952995 | 466 | 0.380591357089 | 502 | 0.380591357089 | 502 |
| lgbm_exclude_level0_selected | 1319 | 0.343442001516 | 453 | 0.369977255497 | 488 | 0.369977255497 | 488 |

Detail files:
- `/root/gsm8k_single_language_experiment/zul_Latn/analysis/test_selection_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/zul_Latn/analysis_lgbm/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/zul_Latn/analysis_lgbm_no_level0/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/zul_Latn/eval/test_selected_metric_summary.json`
