# sin_Sinh Test Metric Comparison

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average | 7914 | 0.280010108668 | 2216 | 0.315137730604 | 2494 | 0.315137730604 | 2494 |
| original_variant_v0 | 1319 | 0.291887793783 | 385 | 0.329037149356 | 434 | 0.329037149356 | 434 |
| sid_rules_selected | 1319 | 0.349507202426 | 461 | 0.385898407885 | 509 | 0.385898407885 | 509 |
| lgbm_all_levels_selected | 1319 | 0.358605003791 | 473 | 0.391963608795 | 517 | 0.391963608795 | 517 |
| lgbm_exclude_level0_selected | 1319 | 0.358605003791 | 473 | 0.391963608795 | 517 | 0.391963608795 | 517 |

Detail files:
- `/root/gsm8k_single_language_experiment/sin_Sinh/analysis/test_selection_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/sin_Sinh/analysis_lgbm/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/sin_Sinh/analysis_lgbm_no_level0/test_selection_lgbm_with_eval_metrics.parquet`
- `/root/gsm8k_single_language_experiment/sin_Sinh/eval/test_selected_metric_summary.json`
