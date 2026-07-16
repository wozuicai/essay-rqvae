# swh_Latn Eval Metric Comparison

Last updated: 2026-07-15 12:07:51 UTC

## What Changed

The original `prediction` / `correct` columns are strict-format GSM8K metrics.
They only parse answers from explicit final-answer markers:

```text
####
\boxed{...}
final answer is ...
answer is ...
```

That behavior is preserved for backward compatibility. SID-rule analysis and
LightGBM selector results produced so far still use this strict `correct`
column.

The eval merge step now also writes relaxed numeric parsing columns:

```text
strict_prediction
strict_correct
relaxed_prediction
relaxed_correct
strict_else_relaxed_prediction
strict_else_relaxed_correct
```

## Final Metrics

Rows:

```text
num_rows = 52752
missing_rows = 0
```

Strict-format GSM8K accuracy:

```text
strict_format_accuracy = 0.48650288140734
strict_train_accuracy = 0.48846960167714887
strict_test_accuracy = 0.47536012130401817
strict_prediction_none = 13842
strict_prediction_none_rate = 0.26239763421292084
```

Relaxed last-number-only accuracy:

```text
relaxed_last_number_accuracy = 0.5141226872914771
relaxed_train_accuracy = 0.5159462955528793
relaxed_test_accuracy = 0.5037907505686126
relaxed_prediction_none = 24
relaxed_prediction_none_rate = 0.00045495905368516835
```

Strict-else-relaxed accuracy:

```text
strict_else_relaxed_accuracy = 0.513971034273582
strict_else_relaxed_train_accuracy = 0.5157901779740399
strict_else_relaxed_test_accuracy = 0.5036643922163255
format_failure_recovered_correct = 1449
```

## Interpretation

The strict metric is the EleutherAI/GSM8K-style final-answer-format metric. It
mixes mathematical correctness with whether the model emitted a parseable final
answer marker.

The relaxed last-number metric answers a different question: if we ignore final
answer formatting and take the final numeric value in the model output, how
often is that number equal to the target?

For diagnosing format failures, `strict_else_relaxed_accuracy` is the most useful
single number here: it keeps strict predictions when present and only falls back
to the relaxed last number when strict parsing failed. It recovered `1449`
otherwise-wrong rows from strict parse failures.

## Files

```text
/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_results.parquet
/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_summary.json
```

