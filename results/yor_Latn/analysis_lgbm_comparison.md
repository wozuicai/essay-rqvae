# Yoruba SID Selector Comparison

Experiment directory:

```text
/root/gsm8k_single_language_experiment/yor_Latn
```

Strict-format correctness was used for SID-rule and LightGBM training/scoring.

| selector | test accuracy | correct / 1319 |
| --- | ---: | ---: |
| original variant v0 | 0.1683093252463988 | 222 |
| all test variants average | 0.21152388172858225 | 1674 / 7914 variants |
| SID rules selected | 0.3100833965125095 | 409 |
| LightGBM all SID levels | 0.30022744503411675 | 396 |
| LightGBM exclude level0 | 0.2979529946929492 | 393 |

LightGBM settings:

```text
num_boost_round = 200
num_threads = 16
```

Outputs:

```text
/root/gsm8k_single_language_experiment/yor_Latn/analysis_lgbm/analysis_lgbm_summary.json
/root/gsm8k_single_language_experiment/yor_Latn/analysis_lgbm_no_level0/analysis_lgbm_summary.json
```

Interpretation: for `yor_Latn`, the transparent SID-rule selector is ahead of
both LightGBM variants under the strict metric. Excluding level 0 does not help
the LightGBM selector in this run.
