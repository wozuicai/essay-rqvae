# sin_Sinh Aggressive Filtered Test Metric Comparison

This report excludes aggressive high-risk bad `test` source rows only. Original result files are not modified.

- Dropped source rows: `4` / `1319`
- Kept source rows: `1315` / `1319`
- Bad-row details: `/root/gsm8k_single_language_experiment/sin_Sinh/eval/test_bad_source_rows_for_aggressive_filtered_summary.json`

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average_aggressive_filtered | 7890 | 0.2799746514575412 | 2209 | 0.314828897338403 | 2484 | 0.314828897338403 | 2484 |
| original_variant_v0_aggressive_filtered | 1315 | 0.29277566539923955 | 385 | 0.3300380228136882 | 434 | 0.3300380228136882 | 434 |
| sid_rules_selected_aggressive_filtered | 1315 | 0.34980988593155893 | 460 | 0.38479087452471483 | 506 | 0.38479087452471483 | 506 |
| lgbm_all_levels_selected_aggressive_filtered | 1315 | 0.3574144486692015 | 470 | 0.39011406844106467 | 513 | 0.39011406844106467 | 513 |
| lgbm_exclude_level0_selected_aggressive_filtered | 1315 | 0.3574144486692015 | 470 | 0.39011406844106467 | 513 | 0.39011406844106467 | 513 |
