# som_Latn Test Metric Comparison

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average | 7914 | 0.347611827142 | 2751 | 0.373768006065 | 2958 | 0.373641647713 | 2957 |
| original_variant_v0 | 1319 | 0.378316906748 | 499 | 0.400303260045 | 528 | 0.400303260045 | 528 |
| sid_rules_selected | 1319 | 0.410159211524 | 541 | 0.433661865049 | 572 | 0.433661865049 | 572 |
| lgbm_all_levels_selected | 1319 | 0.416224412434 | 549 | 0.439727065959 | 580 | 0.439727065959 | 580 |
| lgbm_exclude_level0_selected | 1319 | 0.416224412434 | 549 | 0.439727065959 | 580 | 0.439727065959 | 580 |

Detail files:
- `/root/gsm8k_single_language_experiment/som_Latn/analysis/test_selection_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/som_Latn/analysis_lgbm/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/som_Latn/analysis_lgbm_no_level0/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/som_Latn/eval/test_selected_metric_summary.json`
