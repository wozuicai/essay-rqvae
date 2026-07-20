# npi_Deva Filtered Test Metric Comparison

This report excludes high-confidence bad `test` source rows only. Original result files are not modified.

- Dropped source rows: `40` / `1319`
- Kept source rows: `1279` / `1319`
- Bad-row details: `/root/gsm8k_single_language_experiment/npi_Deva/eval/test_bad_source_rows_for_filtered_summary.json`

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average_filtered | 7674 | 0.32694813656502475 | 2509 | 0.3623924941360438 | 2781 | 0.36226218399791504 | 2780 |
| original_variant_v0_filtered | 1279 | 0.34010946051602814 | 435 | 0.3713838936669273 | 475 | 0.3713838936669273 | 475 |
| sid_rules_selected_filtered | 1279 | 0.39014855355746675 | 499 | 0.4292415949960907 | 549 | 0.4292415949960907 | 549 |
| lgbm_all_levels_selected_filtered | 1279 | 0.37998436278342457 | 486 | 0.40969507427677876 | 524 | 0.4104769351055512 | 525 |
| lgbm_exclude_level0_selected_filtered | 1279 | 0.37998436278342457 | 486 | 0.40969507427677876 | 524 | 0.4104769351055512 | 525 |
