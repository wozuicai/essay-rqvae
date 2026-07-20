# zul_Latn Aggressive Filtered Test Metric Comparison

This report excludes aggressive high-risk bad `test` source rows only. Original result files are not modified.

- Dropped source rows: `0` / `1319`
- Kept source rows: `1319` / `1319`
- Bad-row details: `/root/gsm8k_single_language_experiment/zul_Latn/eval/test_bad_source_rows_for_aggressive_filtered_summary.json`

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average_aggressive_filtered | 7914 | 0.28936062673742735 | 2290 | 0.31374778872883496 | 2483 | 0.31374778872883496 | 2483 |
| original_variant_v0_aggressive_filtered | 1319 | 0.266868840030326 | 352 | 0.2896133434420015 | 382 | 0.2896133434420015 | 382 |
| sid_rules_selected_aggressive_filtered | 1319 | 0.33813495072024263 | 446 | 0.3646702047005307 | 481 | 0.3646702047005307 | 481 |
| lgbm_all_levels_selected_aggressive_filtered | 1319 | 0.35329795299469297 | 466 | 0.38059135708870356 | 502 | 0.38059135708870356 | 502 |
| lgbm_exclude_level0_selected_aggressive_filtered | 1319 | 0.3434420015163002 | 453 | 0.36997725549658833 | 488 | 0.36997725549658833 | 488 |
