# npi_Deva SID Selector Comparison

| selector | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all test variants average | 7914 | 0.323351023503 | 2559 | 0.358352287086 | 2836 | 0.358225928734 | 2835 |
| original variant v0 | 1319 | 0.329795299469 | 435 | 0.361637604246 | 477 | 0.361637604246 | 477 |
| SID rules selected | 1319 | 0.388172858226 | 512 | 0.426838514026 | 563 | 0.426838514026 | 563 |
| LightGBM all SID levels | 1319 | 0.378316906748 | 499 | 0.407884761183 | 538 | 0.408642911296 | 539 |
| LightGBM exclude level0 | 1319 | 0.378316906748 | 499 | 0.407884761183 | 538 | 0.408642911296 | 539 |

Notes:
- Transparent SID rules outperform both LightGBM variants on strict and strict-else-relaxed selected-test accuracy.
- Both LightGBM variants selected the same number of strict-correct cases in this run.
- Nepali rewrite generation used `716` fallback-repaired rewrite records to keep the variant table complete; interpret rewrite diversity accordingly.

Detail files:
- `/root/gsm8k_single_language_experiment/npi_Deva/eval/test_selected_metric_summary.json`
- `/root/gsm8k_single_language_experiment/npi_Deva/eval/test_selected_metric_comparison.md`
- `/root/gsm8k_single_language_experiment/npi_Deva/analysis/analysis_summary.json`
- `/root/gsm8k_single_language_experiment/npi_Deva/analysis_lgbm/analysis_lgbm_summary.json`
- `/root/gsm8k_single_language_experiment/npi_Deva/analysis_lgbm_no_level0/analysis_lgbm_summary.json`
