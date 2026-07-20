# npi_Deva Test Metric Comparison

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average | 7914 | 0.323351023503 | 2559 | 0.358352287086 | 2836 | 0.358225928734 | 2835 |
| original_variant_v0 | 1319 | 0.329795299469 | 435 | 0.361637604246 | 477 | 0.361637604246 | 477 |
| sid_rules_selected | 1319 | 0.388172858226 | 512 | 0.426838514026 | 563 | 0.426838514026 | 563 |
| lgbm_all_levels_selected | 1319 | 0.378316906748 | 499 | 0.407884761183 | 538 | 0.408642911296 | 539 |
| lgbm_exclude_level0_selected | 1319 | 0.378316906748 | 499 | 0.407884761183 | 538 | 0.408642911296 | 539 |

Detail files:
- `/root/gsm8k_single_language_experiment/npi_Deva/analysis/test_selection_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/npi_Deva/analysis_lgbm/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/npi_Deva/analysis_lgbm_no_level0/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/npi_Deva/eval/test_selected_metric_summary.json`
