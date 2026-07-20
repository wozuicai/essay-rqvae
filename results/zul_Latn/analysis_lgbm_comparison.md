# Zulu SID Selector Comparison

Strict-format correctness.

| selector | test accuracy | correct / 1319 |
| --- | ---: | ---: |
| original variant v0 | 0.266868840030 | 352 |
| all test variants average | 0.289360626737 |  |
| SID rules selected | 0.338134950720 | 446 |
| LightGBM all SID levels | 0.353297952995 | 466 |
| LightGBM exclude level0 | 0.343442001516 | 453 |

- Significant SID rules: `870` from `3184` bucket tests.
- LightGBM all-level test AUC: `0.7035339810046773`; exclude-level0 test AUC: `0.7047314767652048`.
