# yor_Latn Aggressive Filtered Test Metric Comparison

This report excludes aggressive high-risk bad `test` source rows only. Original result files are not modified.

- Dropped source rows: `0` / `1319`
- Kept source rows: `1319` / `1319`
- Bad-row details: `/root/gsm8k_single_language_experiment/yor_Latn/eval/test_bad_source_rows_for_aggressive_filtered_summary.json`

| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_variants_average_aggressive_filtered | 7914 | 0.21152388172858225 | 1674 | 0.23313115996967398 | 1845 | 0.2332575183219611 | 1846 |
| original_variant_v0_aggressive_filtered | 1319 | 0.1683093252463988 | 222 | 0.19408642911296436 | 256 | 0.19408642911296436 | 256 |
| sid_rules_selected_aggressive_filtered | 1319 | 0.3100833965125095 | 409 | 0.33434420015163 | 441 | 0.33434420015163 | 441 |
| lgbm_all_levels_selected_aggressive_filtered | 1319 | 0.30022744503411675 | 396 | 0.32752084912812734 | 432 | 0.32752084912812734 | 432 |
| lgbm_exclude_level0_selected_aggressive_filtered | 1319 | 0.2979529946929492 | 393 | 0.3252463987869598 | 429 | 0.3252463987869598 | 429 |
