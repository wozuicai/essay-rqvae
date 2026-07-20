# npi_Deva Aggressive Filtered Test Metric Comparison

This report excludes aggressive high-risk bad `test` source rows only. Original result files are not modified.

- Dropped source rows: `43` / `1319`
- Kept source rows: `1276` / `1319`
- Bad-row details: `/root/gsm8k_single_language_experiment/npi_Deva/eval/test_bad_source_rows_for_aggressive_filtered_summary.json`

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average_aggressive_filtered | 7656 | 0.3270637408568443 | 2504 | 0.3625914315569488 | 2776 | 0.36246081504702193 | 2775 |
| original_variant_v0_aggressive_filtered | 1276 | 0.3401253918495298 | 434 | 0.3714733542319749 | 474 | 0.3714733542319749 | 474 |
| sid_rules_selected_aggressive_filtered | 1276 | 0.390282131661442 | 498 | 0.42946708463949845 | 548 | 0.42946708463949845 | 548 |
| lgbm_all_levels_selected_aggressive_filtered | 1276 | 0.38087774294670845 | 486 | 0.4106583072100313 | 524 | 0.4114420062695925 | 525 |
| lgbm_exclude_level0_selected_aggressive_filtered | 1276 | 0.38087774294670845 | 486 | 0.4106583072100313 | 524 | 0.4114420062695925 | 525 |
