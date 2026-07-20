# swh_Latn Test Metric Comparison

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average | 7914 | 0.475360121304 | 3762 | 0.503790750569 | 3987 | 0.503664392216 | 3986 |
| original_variant_v0 | 1319 | 0.498104624716 | 657 | 0.520849128127 | 687 | 0.520849128127 | 687 |
| sid_rules_selected | 1319 | 0.552691432904 | 729 | 0.576952236543 | 761 | 0.576952236543 | 761 |
| lgbm_all_levels_selected | 1319 | 0.553449583017 | 730 | 0.580742987111 | 766 | 0.580742987111 | 766 |
| lgbm_exclude_level0_selected | 1319 | 0.551933282790 | 728 | 0.579226686884 | 764 | 0.579226686884 | 764 |

Detail files:
- `/root/gsm8k_single_language_experiment/swh_Latn/analysis/test_selection_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/swh_Latn/eval/test_selected_metric_summary.json`
