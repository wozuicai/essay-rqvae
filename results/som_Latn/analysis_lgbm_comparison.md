# Somali SID Selector Comparison

Strict-format correctness.

| selector | test accuracy | correct / 1319 |
| --- | ---: | ---: |
| original variant v0 | 0.378316906748 | 499 |
| all test variants average | 0.347611827142 |  |
| SID rules selected | 0.410159211524 | 541 |
| LightGBM all SID levels | 0.416224412434 | 549 |
| LightGBM exclude level0 | 0.416224412434 | 549 |

- Significant SID rules: `704` from `2750` bucket tests.
- LightGBM all-level test AUC: `0.7003218170167974`; exclude-level0 test AUC: `0.7003218170167974`.
