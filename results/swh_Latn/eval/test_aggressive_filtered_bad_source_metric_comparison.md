# swh_Latn Aggressive Filtered Test Metric Comparison

This report excludes aggressive high-risk bad `test` source rows only. Original result files are not modified.

- Dropped source rows: `1` / `1319`
- Kept source rows: `1318` / `1319`
- Bad-row details: `/root/gsm8k_single_language_experiment/swh_Latn/eval/test_bad_source_rows_for_aggressive_filtered_summary.json`

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average_aggressive_filtered | 7908 | 0.4757207890743551 | 3762 | 0.5041729893778453 | 3987 | 0.5040465351542741 | 3986 |
| original_variant_v0_aggressive_filtered | 1318 | 0.4984825493171472 | 657 | 0.5212443095599393 | 687 | 0.5212443095599393 | 687 |
| sid_rules_selected_aggressive_filtered | 1318 | 0.5531107738998483 | 729 | 0.5773899848254932 | 761 | 0.5773899848254932 | 761 |
| lgbm_all_levels_selected_aggressive_filtered | 1318 | 0.5538694992412747 | 730 | 0.5811836115326252 | 766 | 0.5811836115326252 | 766 |
| lgbm_exclude_level0_selected_aggressive_filtered | 1318 | 0.5523520485584219 | 728 | 0.5796661608497724 | 764 | 0.5796661608497724 | 764 |
