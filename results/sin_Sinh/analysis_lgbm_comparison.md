# Sinhala SID Selector Comparison

Strict-format correctness.

| selector | test accuracy | correct / 1319 |
| --- | ---: | ---: |
| original variant v0 | 0.291887793783 | 385 |
| all test variants average | 0.280010108668 |  |
| SID rules selected | 0.349507202426 | 461 |
| LightGBM all SID levels | 0.358605003791 | 473 |
| LightGBM exclude level0 | 0.358605003791 | 473 |

- Significant SID rules: `873` from `3099` bucket tests.
- LightGBM all-level test AUC: `0.7220465680528858`; exclude-level0 test AUC: `0.7220465680528858`.
