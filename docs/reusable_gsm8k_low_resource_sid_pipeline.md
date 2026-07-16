# Reusable GSM8K Low-Resource Rewrite + SID Selection Pipeline

This document describes the reusable workflow that was run for
`swh_Latn` under:

```text
/root/gsm8k_single_language_experiment/swh_Latn
```

It is written as a template for running another low-resource language with the
same setup.

## 0. Inputs and Assumptions

Required inputs:

```text
/root/gsm8k
/root/gsm8k_nllb_direct/<LANG>
/root/nllb-200-1.3B
/root/qwen3.5-9B-instruct
/mnt/bn/search-gec-agentic-search-useast1b/guo/gpt-oss-120B
/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe
/root/run_gsm8k_single_language_experiment.py
```

Worker assumptions:

```text
8 x H100
/root shared with the worker
use /home/tiger/.ssh/id_rsa for SSH
recover worker SSH port from /home/tiger/.ssh/known_hosts
```

Useful environment:

```bash
PY=/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python
SCRIPT=/root/run_gsm8k_single_language_experiment.py
OUT=/root/gsm8k_single_language_experiment/<LANG>
```

For the completed run:

```bash
LANG=swh_Latn
LANG_NAME=Swahili
OUT=/root/gsm8k_single_language_experiment/swh_Latn
```

## 1. Prepare One-Language Source Table

Build a table with original low-resource questions and GSM8K answers.

```bash
NO_COLOR=1 TERM=dumb mlx worker login <WORKER_ID> -- \
  "cd /root && $PY $SCRIPT prepare \
    --lang $LANG \
    --lang-name $LANG_NAME \
    --out-dir $OUT"
```

Expected output:

```text
$OUT/source.parquet
$OUT/source.jsonl
$OUT/prepare_meta.json
```

Expected counts for GSM8K main split:

```text
train = 7473
test  = 1319
total = 8792
```

## 2. English Rewrite with gpt-oss

The rewrite should be done in English first, not directly in the low-resource
language.

Goal:

```text
For every original English GSM8K question, produce exactly 5 meaning-preserving
English rewrites.
```

Use vLLM with one process per GPU rather than tensor parallelism. `gpt-oss-120B`
fits on one H100 with MXFP4. Tensor parallel startup was less reliable in this
environment.

Example 8-GPU launcher:

```bash
ssh -i /home/tiger/.ssh/id_rsa -p <PORT> tiger@<WORKER_IPV6> '
cd /root
mkdir -p '"$OUT"'/rewrites_en/logs
nohup bash -lc '"'"'
set -euo pipefail
PY=/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python
SCRIPT=/root/run_gsm8k_single_language_experiment.py
OUT=/root/gsm8k_single_language_experiment/<LANG>
LOGDIR=$OUT/rewrites_en/logs
for r in 0 1 2 3 4 5 6 7; do
  (
    cd /root
    export CUDA_VISIBLE_DEVICES=$r
    export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
    $PY $SCRIPT rewrite-english \
      --lang <LANG> \
      --lang-name <LANG_NAME> \
      --out-dir $OUT \
      --rank $r \
      --world-size 8 \
      --batch-size 16 \
      --tensor-parallel-size 1 \
      --gpu-memory-utilization 0.88 \
      --max-model-len 4096 \
      --max-num-seqs 16 \
      --guided-json \
      --temperature 0.45 \
      --top-p 0.9 \
      --num-candidates 2
  ) > $LOGDIR/rewrite_rank${r}.log 2>&1 &
done
wait
'"'"' > '"$OUT"'/rewrites_en/logs/rewrite_all.out 2>&1 &
'
```

Outputs:

```text
$OUT/rewrites_en/english_rewrite_records_rank00_of_08.jsonl
...
$OUT/rewrites_en/english_rewrite_records_rank07_of_08.jsonl
```

Each record must have:

```json
{
  "status": "ok",
  "split": "train",
  "source_idx": 0,
  "english_question": "...",
  "rewrites": ["...", "...", "...", "...", "..."]
}
```

## 3. Retry Failed English Rewrites

After each rewrite run, count valid records by `(split, source_idx)`.

Write a missing manifest:

```text
$OUT/rewrites_en/missing_after_rerunN.jsonl
```

Shape:

```json
{"split": "train", "source_idx": 123}
```

Re-run only missing keys:

```bash
$PY $SCRIPT rewrite-english \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT \
  --only-missing-file $OUT/rewrites_en/missing_after_rerunN.jsonl \
  --force-rewrite \
  --rank <RANK> \
  --world-size 8 \
  --batch-size 8 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.88 \
  --max-model-len 4096 \
  --max-num-seqs 8 \
  --guided-json \
  --temperature 0.2 \
  --top-p 0.85 \
  --num-candidates 3 \
  --max-tokens 768
```

For harder cases, use more candidates and smaller batches:

```bash
--batch-size 4
--max-num-seqs 4
--temperature 0.15
--top-p 0.8
--num-candidates 10
--max-tokens 1200
```

## 4. Translate English Rewrites with NLLB

Translate valid English rewrites to the target low-resource language:

```bash
NO_COLOR=1 TERM=dumb mlx worker login <WORKER_ID> -- \
  "cd /root && CUDA_VISIBLE_DEVICES=0 \
   LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH \
   $PY $SCRIPT translate-rewrites \
     --lang $LANG \
     --lang-name $LANG_NAME \
     --out-dir $OUT \
     --device cuda \
     --batch-size 128 \
     --source-max-length 512 \
     --target-max-length 512"
```

For targeted translation of a retry manifest:

```bash
$PY $SCRIPT translate-rewrites \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT \
  --device cuda \
  --batch-size 128 \
  --source-max-length 512 \
  --target-max-length 512 \
  --force-keys-file <manifest.jsonl>
```

Output:

```text
$OUT/rewrites/rewrite_records.jsonl
$OUT/.cache/english_rewrites__<LANG>.jsonl
```

Final rewrite file requirements:

```text
8792 records
8792 unique (split, source_idx)
status=ok for all
5 rewrites per record
no Chinese text
no structural/template fallback records
```

## 5. Manual Final Tail

If repeated `gpt-oss + NLLB` attempts leave only a small tail, rewrite those
remaining records manually.

Rules:

```text
Write in the target low-resource language.
Do not use fixed prefix templates.
Preserve meaning.
Preserve all numbers and named entities.
Provide exactly 5 natural rewrites.
```

For this run, the final file ended with:

```text
8557 records from gpt-oss-120B + nllb-200-1.3B
235 records from true_manual_swahili_rewrite_by_agent
0 structural/template records
0 bad records
0 Chinese contamination
```

Manual batch files were stored as:

```text
/root/manual_true_rewrites_batch*.jsonl
```

Bad drafts to avoid:

```text
/root/manual_true_rewrites_batch007.jsonl
```

That file contained Chinese and was never written to the final active
`rewrite_records.jsonl`.

## 6. Rebuild Variants

After final rewrites are clean, delete stale downstream artifacts before
refreshing:

```bash
rm -rf \
  $OUT/variants \
  $OUT/hidden \
  $OUT/rqvae \
  $OUT/eval \
  $OUT/analysis
```

Build variants:

```bash
$PY $SCRIPT build-variants \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT
```

Expected:

```text
$OUT/variants/variants.parquet
shape = 52752 x 8
train = 44838
test = 7914
variant_idx = 0..5 for every source
```

## 7. Extract Qwen Last-Token Hidden States

Use Qwen3.5:

```text
/root/qwen3.5-9B-instruct
```

The model has:

```text
32 layers
hidden size 4096
hidden states output = embedding layer + 32 layers = 33
```

Use:

```text
left padding
single forward pass
output_hidden_states=True
no generation
8-way data parallel, one GPU per rank
float16 memmap output
```

8-GPU launcher pattern:

```bash
ssh -i /home/tiger/.ssh/id_rsa -p <PORT> tiger@<WORKER_IPV6> '
cd /root
mkdir -p '"$OUT"'/hidden/logs
nohup bash -lc '"'"'
set -euo pipefail
PY=/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python
SCRIPT=/root/run_gsm8k_single_language_experiment.py
OUT=/root/gsm8k_single_language_experiment/<LANG>
LOGDIR=$OUT/hidden/logs
for r in 0 1 2 3 4 5 6 7; do
  (
    cd /root
    export CUDA_VISIBLE_DEVICES=$r
    export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
    $PY $SCRIPT extract-hidden \
      --lang <LANG> \
      --lang-name <LANG_NAME> \
      --out-dir $OUT \
      --qwen-model /root/qwen3.5-9B-instruct \
      --rank $r \
      --world-size 8 \
      --batch-size 16 \
      --max-length 1024 \
      --overwrite
  ) > $LOGDIR/extract_rank${r}.log 2>&1 &
done
wait
'"'"' > '"$OUT"'/hidden/logs/extract_all.out 2>&1 &
'
```

Merge hidden shards:

```bash
$PY $SCRIPT merge-hidden \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT \
  --chunk-size 512
```

Expected:

```text
$OUT/hidden/hidden_states.float16.memmap
shape = [52752, 33, 4096]
missing_rows = 0
```

## 8. Train RQ-VAE

Use one configuration, no sweep:

```bash
$PY $SCRIPT train-rqvae \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT \
  --device cuda \
  --latent-dim 256 \
  --num-codebooks 3 \
  --codebook-size 256 \
  --beta-commit 0.25 \
  --epochs 8 \
  --batch-size 2048 \
  --max-val-batches 200 \
  --num-workers 0
```

For the completed run:

```text
train_variant_count = 44838
train_embedding_count = 1479654
final_val_mse = 4.6805269569934656e-05
```

Output:

```text
$OUT/rqvae/model.pt
$OUT/rqvae/train_config.json
$OUT/rqvae/train_history.json
```

## 9. Encode SIDs and Review RQ-VAE Metrics

Encode every variant/layer embedding:

```bash
$PY $SCRIPT encode-sids \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT \
  --device cuda \
  --batch-size 4096
```

Expected:

```text
$OUT/rqvae/sids.uint16.memmap
shape = [52752, 33, 3]
$OUT/rqvae/sid_metrics.json
```

Metrics to inspect:

```text
MSE
relative L2
codebook usage
dead code ratio
perplexity
residual norm curve
entropy
```

Observed caveat in this run:

```text
level_0_usage_mean = 0.006036931818181818
level_1_usage_mean = 0.18217329545454544
level_2_usage_mean = 0.6040482954545454
```

Level 0 is severely collapsed. Treat level 0 SID rules with caution. Consider
rerunning analysis with `level != 0` if needed.

## 10. Evaluation

Use a GSM8K-style 5-shot prompt:

```text
Question: ...
Answer: ... #### N

Question: ...
Answer:
```

The raw EleutherAI `gsm8k.yaml` uses:

```text
doc_to_text = "Question: {{question}}\nAnswer:"
num_fewshot = 5
strict regex = #### (\\-?[0-9\\.\\,]+)
```

Qwen native thinking caused very long hidden reasoning and often did not reach
`####` within practical token limits. For the full run, the Qwen chat template
was called with:

```text
enable_thinking=False
```

This keeps the GSM8K few-shot `####` format while making generation feasible.

Launcher:

```text
/root/launch_swh_eval.sh
```

Settings:

```text
world_size = 8
batch_size = 8
max_input_length = 2048
max_new_tokens = 256
```

Output:

```text
$OUT/eval/eval_rank00_of_08.jsonl
...
$OUT/eval/eval_rank07_of_08.jsonl
```

Merge:

```bash
$PY $SCRIPT merge-eval \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT
```

Final run:

```text
eval rows = 52752
missing_rows = 0
strict_format_accuracy = 0.48650288140734
strict_train_accuracy = 0.48846960167714887
strict_test_accuracy = 0.47536012130401817
strict_prediction_none = 13842
strict_prediction_none_rate = 0.26239763421292084

relaxed_last_number_accuracy = 0.5141226872914771
relaxed_train_accuracy = 0.5159462955528793
relaxed_test_accuracy = 0.5037907505686126

strict_else_relaxed_accuracy = 0.513971034273582
strict_else_relaxed_train_accuracy = 0.5157901779740399
strict_else_relaxed_test_accuracy = 0.5036643922163255
format_failure_recovered_correct = 1449
```

Metric meanings:

- `strict_format_accuracy` is the GSM8K-style metric. It only accepts explicit
  final-answer markers: `####`, `\boxed{}`, `answer is`, or `final answer is`.
- `relaxed_last_number_accuracy` ignores final-answer formatting and takes the
  final numeric value in the model output.
- `strict_else_relaxed_accuracy` uses the strict answer when present and falls
  back to the relaxed last number only when strict parsing fails.
- The `prediction` and `correct` columns are kept as strict-format aliases for
  backward compatibility.
- The SID-rule and LightGBM selector steps below use strict `correct` unless
  explicitly modified.

## 11. Find SID Rules and Select Test Rewrite

Run:

```bash
$PY $SCRIPT analyze \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT \
  --min-bucket-n 100 \
  --fdr 0.05
```

The analysis does:

1. Compute global/train baseline accuracy.
2. For every `(layer, level, sid)` bucket:
   - count `n`
   - count `correct`
   - compute conditional accuracy
   - compute uplift over baseline
   - compute Wilson lower bound
   - run Fisher exact test
   - apply Benjamini-Hochberg FDR correction
3. Keep rules where:
   - `q_value <= 0.05`
   - `wilson_lower > baseline_train_accuracy`
   - `uplift > 0`
   - `n >= min_bucket_n`
4. For each test source question, score its 6 variants by summing weights of
   matched significant SID rules.
5. Select the highest-scoring variant.

Rule weight:

```python
weight = uplift * max(1.0, -log10(max(q_value, 1e-300)))
```

Outputs:

```text
$OUT/analysis/sid_buckets.parquet
$OUT/analysis/significant_sid_rules.parquet
$OUT/analysis/test_selection.parquet
$OUT/analysis/analysis_summary.json
```

CSV copies were also written for easy viewing:

```text
$OUT/analysis/sid_buckets.csv
$OUT/analysis/significant_sid_rules.csv
$OUT/analysis/test_selection.csv
```

Final run:

```text
baseline_all_accuracy = 0.48650288140734
baseline_train_accuracy = 0.48846960167714887
test_original_accuracy = 0.4981046247156937
test_all_variant_accuracy = 0.47536012130401817
test_selected_accuracy = 0.5526914329037149
num_bucket_tests = 2888
num_significant_rules = 895
```

## 12. Optional LightGBM SID Selector

The rule selector is transparent but hand-scored. A supervised tree model can
also learn correctness from the same SID features.

Script:

```text
/root/train_lgbm_sid_selector.py
```

Run all SID levels:

```bash
$PY /root/train_lgbm_sid_selector.py \
  --out-dir $OUT \
  --num-boost-round 200 \
  --num-threads 16
```

Run without collapsed level 0:

```bash
$PY /root/train_lgbm_sid_selector.py \
  --out-dir $OUT \
  --num-boost-round 200 \
  --num-threads 16 \
  --exclude-level0
```

Notes:

- Each variant is one training example.
- Features are categorical SID ids from `(layer, codebook_level)`.
- Label is the aligned eval correctness for that variant.
- For each test source question, score its six variants and select the highest
  LightGBM score.
- Avoid launching many LightGBM jobs with `num_threads=-1`; on the current worker
  that made the 600-round runs slow. Use explicit `--num-threads`.

Outputs:

```text
$OUT/analysis_lgbm/analysis_lgbm_summary.json
$OUT/analysis_lgbm/test_variant_scores.parquet
$OUT/analysis_lgbm/test_variant_scores.csv
$OUT/analysis_lgbm/test_selection_lgbm.parquet
$OUT/analysis_lgbm/test_selection_lgbm.csv
$OUT/analysis_lgbm/feature_importance.csv
$OUT/analysis_lgbm/model.txt

$OUT/analysis_lgbm_no_level0/analysis_lgbm_summary.json
$OUT/analysis_lgbm_no_level0/test_variant_scores.parquet
$OUT/analysis_lgbm_no_level0/test_variant_scores.csv
$OUT/analysis_lgbm_no_level0/test_selection_lgbm.parquet
$OUT/analysis_lgbm_no_level0/test_selection_lgbm.csv
$OUT/analysis_lgbm_no_level0/feature_importance.csv
$OUT/analysis_lgbm_no_level0/model.txt
```

Final swh_Latn run, strict-format selector results:

```text
test_original_accuracy = 0.4981046247156937
test_selected_accuracy_by_sid_rules = 0.5526914329037149
test_selected_accuracy_by_lgbm_all_levels = 0.5534495830174374
test_selected_accuracy_by_lgbm_exclude_level0 = 0.5519332827899924

correct_test_questions:
  original = 657/1319
  sid_rules = 729/1319
  lgbm_all_levels = 730/1319
  lgbm_exclude_level0 = 728/1319
```

The selectors above were trained or scored using strict `correct`. After adding
the relaxed eval columns, the same selected test variants score as follows:

| test setting | n | strict acc | strict correct | relaxed last-number acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all test variants average | 7914 | 0.475360121304 | 3762 | 0.503790750569 | 3987 | 0.503664392216 | 3986 |
| original variant v0 | 1319 | 0.498104624716 | 657 | 0.520849128127 | 687 | 0.520849128127 | 687 |
| SID rules selected | 1319 | 0.552691432904 | 729 | 0.576952236543 | 761 | 0.576952236543 | 761 |
| LightGBM all SID levels | 1319 | 0.553449583017 | 730 | 0.580742987111 | 766 | 0.580742987111 | 766 |
| LightGBM exclude level0 | 1319 | 0.551933282790 | 728 | 0.579226686884 | 764 | 0.579226686884 | 764 |

Compared with the original v0 test question, the selected variants improve by:

| selector | strict correct delta | relaxed correct delta | strict-else-relaxed correct delta |
| --- | ---: | ---: | ---: |
| SID rules selected | +72 | +74 | +74 |
| LightGBM all SID levels | +73 | +79 | +79 |
| LightGBM exclude level0 | +71 | +77 | +77 |

Interpretation for this run: level 0 is still collapsed and should be treated
cautiously in human-readable rules, but excluding it did not improve LightGBM
test-question selection. Under the relaxed and strict-else-relaxed metrics,
all-level LightGBM is also ahead of the SID-rule selector by 5 test questions.

## 13. Final Audit

Run:

```bash
$PY $SCRIPT audit \
  --lang $LANG \
  --lang-name $LANG_NAME \
  --out-dir $OUT
```

Expected:

```text
$OUT/audit_report.json
ok = true
```

For this run:

```text
rewrite_records_complete = true
variant_counts = true
hidden_states = true
sids = true
eval_results = true
analysis = true
```
