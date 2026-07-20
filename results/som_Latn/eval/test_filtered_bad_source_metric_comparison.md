# som_Latn Filtered Test Metric Comparison

This report excludes high-confidence bad `test` source rows only. Original result files are not modified.

- Dropped source rows: `0` / `1319`
- Kept source rows: `1319` / `1319`
- Bad-row details: `/root/gsm8k_single_language_experiment/som_Latn/eval/test_bad_source_rows_for_filtered_summary.json`

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average_filtered | 7914 | 0.3476118271417741 | 2751 | 0.3737680060652009 | 2958 | 0.3736416477129138 | 2957 |
| original_variant_v0_filtered | 1319 | 0.378316906747536 | 499 | 0.400303260045489 | 528 | 0.400303260045489 | 528 |
| sid_rules_selected_filtered | 1319 | 0.41015921152388174 | 541 | 0.4336618650492798 | 572 | 0.4336618650492798 | 572 |
| lgbm_all_levels_selected_filtered | 1319 | 0.4162244124336619 | 549 | 0.4397270659590599 | 580 | 0.4397270659590599 | 580 |
| lgbm_exclude_level0_selected_filtered | 1319 | 0.4162244124336619 | 549 | 0.4397270659590599 | 580 | 0.4397270659590599 | 580 |
