# swh_Latn GSM8K Rewrite Pipeline Notes

Last updated: 2026-07-14 16:35:49 UTC

## Goal

For the Swahili GSM8K split under `/root/gsm8k_nllb_direct/swh_Latn`, build
5 meaning-preserving rewrites per question, then use those variants for Qwen
hidden-state extraction, RQ-VAE SID encoding, and later evaluation/selection.

The original task requirement was:

- Low-resource question rewrite should be done by first rewriting the English
  GSM8K question.
- Then translate the English rewrites to the low-resource language with
  `/root/nllb-200-1.3B`.
- Each question should have 5 rewrites plus the original question.
- Meaning must stay the same, but wording/order should differ as much as
  possible.

## Worker / Environment

Worker used:

- Worker id: `996354`
- SSH target: `tiger@fdbd:dccd:cdc2:12c8:0:2d4::`
- SSH port: `11373`
- GPU: `8 x H100 80GB`

Important connection pattern:

```bash
ssh -i /home/tiger/.ssh/id_rsa -p 11373 tiger@fdbd:dccd:cdc2:12c8:0:2d4::
```

For `mlx worker login`, use parseable output:

```bash
NO_COLOR=1 TERM=dumb mlx worker login 996354 -- 'hostname && nvidia-smi -L'
```

Main Python environment:

```bash
/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python
```

This venv has:

- `torch 2.7.1+cu128`, CUDA available.
- `transformers 5.12.1`
- `vllm 0.10.1`

System Python has `torch cu130`, but CUDA was not usable with this H100 driver,
so the venv above is the working environment.

## Main Script

The pipeline script is:

```bash
/root/run_gsm8k_single_language_experiment.py
```

It currently supports:

- `prepare`
- `rewrite-english`
- `translate-rewrites`
- `build-variants`
- `extract-hidden`
- `merge-hidden`
- `train-rqvae`
- `encode-sids`
- `eval-generate`
- `merge-eval`
- `analyze`
- `audit`

I changed the progress log path in this script to:

```python
DEFAULT_PROGRESS = Path("/root/gsm8k_query_rewrite_rqvae_worklog.md")
```

I also added:

- `--only-missing-file`
- `--force-rewrite`
- `--force-keys-file`

These were added to enable targeted re-runs of hard rewrite cases.

## Prepared Data

Command:

```bash
NO_COLOR=1 TERM=dumb mlx worker login 996354 -- \
  'cd /root && /mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python \
   /root/run_gsm8k_single_language_experiment.py prepare \
   --lang swh_Latn --lang-name Swahili \
   --out-dir /root/gsm8k_single_language_experiment/swh_Latn'
```

Output:

```text
/root/gsm8k_single_language_experiment/swh_Latn/source.parquet
/root/gsm8k_single_language_experiment/swh_Latn/source.jsonl
/root/gsm8k_single_language_experiment/swh_Latn/prepare_meta.json
```

Counts:

- Train: `7473`
- Test: `1319`
- Total: `8792`

## English Rewrite Stage

Model:

```text
/mnt/bn/search-gec-agentic-search-useast1b/guo/gpt-oss-120B
```

The first attempt used vLLM tensor parallel size `8`, but it failed during
vLLM EngineCore worker initialization. The working strategy was 8-way data
parallel:

- 8 independent vLLM processes.
- One process per H100.
- Each process runs `tensor_parallel_size=1`.
- Sharding is by stable `(rank, world_size)` over the source records.

The working launch pattern was:

```bash
ssh -i /home/tiger/.ssh/id_rsa -p 11373 tiger@fdbd:dccd:cdc2:12c8:0:2d4:: '
cd /root
mkdir -p /root/gsm8k_single_language_experiment/swh_Latn/rewrites_en/logs_rerun1
nohup bash -lc '"'"'
set -euo pipefail
PY=/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python
SCRIPT=/root/run_gsm8k_single_language_experiment.py
OUT=/root/gsm8k_single_language_experiment/swh_Latn
LOGDIR=$OUT/rewrites_en/logs_rerun1
for r in 0 1 2 3 4 5 6 7; do
  (
    cd /root
    export CUDA_VISIBLE_DEVICES=$r
    export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
    $PY $SCRIPT rewrite-english \
      --lang swh_Latn --lang-name Swahili \
      --out-dir $OUT \
      --rank $r --world-size 8 \
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
'"'"' > /root/gsm8k_single_language_experiment/swh_Latn/rewrites_en/logs_rerun1/rewrite_all.out 2>&1 &
'
```

Then a second targeted run was done for the remaining bad cases with:

```bash
--only-missing-file /root/gsm8k_single_language_experiment/swh_Latn/rewrites_en/missing_after_rerun1.jsonl
--batch-size 8
--max-num-seqs 8
--temperature 0.2
--top-p 0.85
--num-candidates 3
--max-tokens 768
```

After filtering and repeated re-runs:

- Valid English rewrite coverage: `8792 / 8792`
- Initial hard cases that needed fallback/manual attention: `403`

## Swahili Translation Stage

Model:

```text
/root/nllb-200-1.3B
```

Command:

```bash
NO_COLOR=1 TERM=dumb mlx worker login 996354 -- \
  'cd /root && CUDA_VISIBLE_DEVICES=0 LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH \
   /mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python \
   /root/run_gsm8k_single_language_experiment.py translate-rewrites \
   --lang swh_Latn --lang-name Swahili \
   --out-dir /root/gsm8k_single_language_experiment/swh_Latn \
   --device cuda \
   --batch-size 128 \
   --source-max-length 512 \
   --target-max-length 512'
```

Output:

```text
/root/gsm8k_single_language_experiment/swh_Latn/rewrites/rewrite_records.jsonl
/root/gsm8k_single_language_experiment/swh_Latn/.cache/english_rewrites__swh_Latn.jsonl
```

After strict validation:

- NLLB produced `8619` immediately valid records.
- `173` records failed strict validation, often because:
  - a proper noun contained English words such as `The`.
  - an activity word like `babysitting` stayed untranslated.
  - a numeric token drifted.

## Current Hard-Case Rewrite Situation

The old fallback approach was not acceptable as final data. The required path
for the remaining hard cases is:

1. Use `gpt-oss-120B` to produce real English rewrites.
2. Translate those English rewrites to Swahili with `/root/nllb-200-1.3B`.
3. Replace the affected records in final `rewrite_records.jsonl`.
4. Validate coverage and bad counts.

Manual Swahili rewriting should only be used if repeated `gpt-oss + NLLB`
attempts leave a small number of hard failures.

Current final file:

```text
/root/gsm8k_single_language_experiment/swh_Latn/rewrites/rewrite_records.jsonl
```

Final rewrite status:

- Total records: `8792`
- Bad records: `0`
- Chinese contamination in final file: `0`
- Normal `gpt-oss-120B + nllb-200-1.3B` records: `8557`
- True manual Swahili rewrites: `235`
- Structural/manual-template records remaining: `0`

Completion audit at `2026-07-14 17:39:26 UTC`:

- Rows in final file: `8792`
- Unique `(split, source_idx)` keys: `8792`
- Expected source keys: `8792`
- Missing keys: `0`
- Extra keys: `0`
- Records with non-`ok` status or not exactly 5 rewrites: `0`
- Chinese contamination: `0`
- `manual_structural_swahili_rewrite_by_agent` records: `0`

Final file:

```text
/root/gsm8k_single_language_experiment/swh_Latn/rewrites/rewrite_records.jsonl
```

Important: the file `/root/manual_true_rewrites_batch007.jsonl` is a bad draft
that accidentally contains Chinese. It was never written to final
`rewrite_records.jsonl`. Do not use it.

Use only Swahili manual batches with `_sw` if both exist.

## Manual Rewrite Workflow

Only use this if the model pipeline leaves a small final tail. To get the next
structural records:

```bash
python3 - <<'PY'
from pathlib import Path
import json, pandas as pd
p=Path('/root/gsm8k_single_language_experiment/swh_Latn/rewrites/rewrite_records.jsonl')
source_sw=pd.read_parquet('/root/gsm8k_single_language_experiment/swh_Latn/source.parquet')
sw={(str(r.split), int(r.source_idx)): str(r.question) for r in source_sw.itertuples(index=False)}
eng={}
for split in ['train','test']:
    df=pd.read_parquet(Path('/root/gsm8k')/'main'/f'{split}-00000-of-00001.parquet')
    for i,row in df.reset_index(drop=True).iterrows():
        eng[(split,int(i))]=str(row['question'])
struct=[]
for line in p.open(encoding='utf-8'):
    rec=json.loads(line)
    if rec.get('model')=='manual_structural_swahili_rewrite_by_agent':
        struct.append((rec['split'], int(rec['source_idx'])))
for key in struct[:10]:
    print('\\nKEY',key)
    print('EN:', eng[key])
    print('SW:', sw[key])
PY
```

For each batch:

1. Write a JSONL file such as:

   ```text
   /root/manual_true_rewrites_batchNNN.jsonl
   ```

2. Each line shape:

   ```json
   {"split":"train","source_idx":123,"rewrites":["...", "...", "...", "...", "..."]}
   ```

3. The rewrites must be Swahili, not Chinese, not English.
4. The rewrites must preserve all numbers and the original meaning.
5. Then write the batch into the final file with the update script pattern used
   in previous batches, setting:

   ```text
   model=true_manual_swahili_rewrite_by_agent
   rewrite_method=semantic manual rewrite by assistant, not template generation
   ```

6. Validate:

   ```bash
   python3 - <<'PY'
   from pathlib import Path
   import json, re
   final=Path('/root/gsm8k_single_language_experiment/swh_Latn/rewrites/rewrite_records.jsonl')
   struct=true=bad=chinese=0
   for line in final.open(encoding='utf-8'):
       rec=json.loads(line)
       if rec.get('model')=='manual_structural_swahili_rewrite_by_agent': struct+=1
       if rec.get('model')=='true_manual_swahili_rewrite_by_agent': true+=1
       if rec.get('status')!='ok' or len(rec.get('rewrites') or [])!=5: bad+=1
       if any(re.search(r'[\\u4e00-\\u9fff]', str(x)) for x in rec.get('rewrites', [])): chinese+=1
   print('struct_remaining', struct, 'true_manual', true, 'bad', bad, 'chinese_in_final', chinese)
   PY
   ```

## Downstream Artifacts Already Built

These were built before all hard cases were manually fixed. They should be
rebuilt after final rewrites are complete.

### Variants

```text
/root/gsm8k_single_language_experiment/swh_Latn/variants/variants.parquet
```

Current old shape:

- `52752 x 8`
- Train: `44838`
- Test: `7914`

### Hidden States

```text
/root/gsm8k_single_language_experiment/swh_Latn/hidden/hidden_states.float16.memmap
```

Current old shape:

- `[52752, 33, 4096]`
- dtype `float16`
- missing rows `0`

### RQ-VAE

Config used:

```text
latent_dim=256
num_codebooks=3
codebook_size=256
beta_commit=0.25
epochs=8
batch_size=2048
normalize=true
```

Model:

```text
/root/gsm8k_single_language_experiment/swh_Latn/rqvae/model.pt
```

Final validation MSE:

```text
5.041540619761994e-05
```

### SID Encoding

```text
/root/gsm8k_single_language_experiment/swh_Latn/rqvae/sids.uint16.memmap
```

Shape:

```text
[52752, 33, 3]
```

Caveat: RQ-VAE level 0 codebook utilization was very poor. Treat level 0
patterns carefully in later analysis.

## Evaluation Status

Evaluation was stopped.

There are partial residual eval shard files under:

```text
/root/gsm8k_single_language_experiment/swh_Latn/eval
```

Do not treat them as official results.

For future eval, align with lm-eval GSM8K behavior. The raw EleutherAI
`gsm8k.yaml` found online has:

- task: `gsm8k`
- `doc_to_text: "Question: {{question}}\\nAnswer:"`
- `num_fewshot: 5`
- strict extraction regex: `#### (\\-?[0-9\\.\\,]+)`
- flexible extraction regex: `(-?[$0-9.,]{2,})|(-?[0-9]+)`

There is also `gsm8k-cot.yaml`:

- task: `gsm8k_cot`
- `doc_to_text: "Q: {{question}}\\n\\nA:"`
- `num_fewshot: 8`
- few-shot chain-of-thought examples ending with `The answer is N.`

The user believes the correct alignment should use the `####` format, so do not
resume the earlier custom eval prompt without confirming the exact eval format.

Refresh eval decision:

- Use a 5-shot GSM8K-style `Question: ...\nAnswer:` prompt.
- Few-shot answers end with `#### N`.
- Keep Qwen thinking enabled.
- Use strict `####` extraction first.
- Do not accept arbitrary numbers from hidden reasoning as predictions.
- Because Qwen can spend hundreds of tokens thinking on Swahili, use a larger
  generation budget for full eval (`max_new_tokens=1024`).


## Refresh Run Status

After final rewrite cleanup, stale downstream directories were deleted:

```text
/root/gsm8k_single_language_experiment/swh_Latn/variants
/root/gsm8k_single_language_experiment/swh_Latn/hidden
/root/gsm8k_single_language_experiment/swh_Latn/rqvae
/root/gsm8k_single_language_experiment/swh_Latn/eval
/root/gsm8k_single_language_experiment/swh_Latn/analysis
```

The final rewrite file was audited before refresh:

```text
rows=8792
unique_keys=8792
ok=8792
bad=0
chinese=0
structural=0
models:
  8557 gpt-oss-120B + nllb-200-1.3B
  235 true_manual_swahili_rewrite_by_agent
```

Variants were rebuilt from the final rewrite file:

```text
/root/gsm8k_single_language_experiment/swh_Latn/variants/variants.parquet
shape=(52752, 8)
train=44838
test=7914
missing_sources=0
```

Hidden extraction was restarted cleanly after an accidental duplicate launch was
stopped and the partial `hidden/` directory was removed. Current active hidden
run:

```text
pid=144439
8 ranks, one rank per H100
batch_size=16
max_length=1024
output=/root/gsm8k_single_language_experiment/swh_Latn/hidden
```


## Refresh Eval Run

Full evaluation was restarted cleanly with a single 8-rank job after duplicate
runs were stopped.

Launcher:

```text
/root/launch_swh_eval.sh
```

Current eval settings:

```text
prompt: 5-shot GSM8K-style Question/Answer examples ending with #### N
qwen chat template: enable_thinking=False for feasible short-answer generation
max_input_length=2048
max_new_tokens=256
batch_size=8
world_size=8
```

Rationale:

- A smoke test with thinking enabled did not reach `####` within 512 tokens on
  Swahili questions.
- With `enable_thinking=False`, the same 5-shot `####` prompt produced parseable
  answers.
- Prediction extraction is strict for explicit final-answer patterns and does
  not accept arbitrary numbers from hidden reasoning.

## Final Completion Status

Final completion audit time: `2026-07-15 09:37:22 UTC`

No worker GPU job is currently running. `nvidia-smi` showed all 8 GPUs idle at
`7 MiB` memory used.

Final active artifacts:

```text
/root/gsm8k_single_language_experiment/swh_Latn/source.parquet
/root/gsm8k_single_language_experiment/swh_Latn/rewrites/rewrite_records.jsonl
/root/gsm8k_single_language_experiment/swh_Latn/variants/variants.parquet
/root/gsm8k_single_language_experiment/swh_Latn/hidden/hidden_states.float16.memmap
/root/gsm8k_single_language_experiment/swh_Latn/rqvae/model.pt
/root/gsm8k_single_language_experiment/swh_Latn/rqvae/sids.uint16.memmap
/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_results.parquet
/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_summary.json
/root/gsm8k_single_language_experiment/swh_Latn/eval/eval_metric_comparison.md
/root/gsm8k_single_language_experiment/swh_Latn/analysis/analysis_summary.json
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/analysis_lgbm_summary.json
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/analysis_lgbm_summary.json
/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_comparison.md
/root/gsm8k_single_language_experiment/swh_Latn/audit_report.json
```

Final rewrite audit:

```text
rows=8792
unique_keys=8792
ok=8792
bad=0
chinese=0
structural=0
models:
  8557 gpt-oss-120B + nllb-200-1.3B
  235 true_manual_swahili_rewrite_by_agent
```

Final variants audit:

```text
shape=(52752, 8)
train=44838
test=7914
each source has variants 0..5
```

Final hidden-state audit:

```text
shape=[52752, 33, 4096]
dtype=float16
missing_rows=0
```

Final RQ-VAE / SID audit:

```text
train_embedding_count=1479654
latent_dim=256
num_codebooks=3
codebook_size=256
beta_commit=0.25
final_val_mse=4.6805269569934656e-05
sids_shape=[52752, 33, 3]
```

Codebook caveat:

```text
level_0_usage_mean=0.006036931818181818
level_1_usage_mean=0.18217329545454544
level_2_usage_mean=0.6040482954545454
```

Level 0 has severe codebook collapse; later interpretation should treat level 0
SID rules cautiously.

Final eval audit:

```text
num_rows=52752
missing_rows=0
strict_format_accuracy=0.48650288140734
strict_train_accuracy=0.48846960167714887
strict_test_accuracy=0.47536012130401817
strict_prediction_none=13842
strict_prediction_none_rate=0.26239763421292084

relaxed_last_number_accuracy=0.5141226872914771
relaxed_train_accuracy=0.5159462955528793
relaxed_test_accuracy=0.5037907505686126
relaxed_prediction_none=24
relaxed_prediction_none_rate=0.00045495905368516835

strict_else_relaxed_accuracy=0.513971034273582
strict_else_relaxed_train_accuracy=0.5157901779740399
strict_else_relaxed_test_accuracy=0.5036643922163255
format_failure_recovered_correct=1449
```

The original `prediction` and `correct` columns are retained as strict-format
GSM8K metrics for backward compatibility. SID-rule analysis and LightGBM
selector outputs above are still based on strict `correct`, not relaxed
last-number correctness.

Final analysis audit:

```text
baseline_all_accuracy=0.48650288140734
baseline_train_accuracy=0.48846960167714887
test_original_accuracy=0.4981046247156937
test_all_variant_accuracy=0.47536012130401817
test_selected_accuracy=0.5526914329037149
num_bucket_tests=2888
num_significant_rules=895
min_bucket_n=100
fdr=0.05
```

Final LightGBM SID-selector audit:

```text
script=/root/train_lgbm_sid_selector.py
num_boost_round=200
num_threads=16

all_levels:
  num_features=99
  train_auc=0.9469978031321118
  test_auc=0.7092131767937975
  test_selected_accuracy=0.5534495830174374
  correct_test_questions=730/1319
  output=/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm/analysis_lgbm_summary.json

exclude_level0:
  num_features=66
  train_auc=0.9470908309670145
  test_auc=0.7105024358789189
  test_selected_accuracy=0.5519332827899924
  correct_test_questions=728/1319
  output=/root/gsm8k_single_language_experiment/swh_Latn/analysis_lgbm_no_level0/analysis_lgbm_summary.json
```

The all-level LightGBM selector is slightly ahead of the SID-rule selector on
this run: `730` correct test questions vs `729`. Excluding level 0 is not better
for final per-question selection here, even though level 0 is collapsed and
should remain suspect for human rule interpretation.

The script audit passed:

```text
/root/gsm8k_single_language_experiment/swh_Latn/audit_report.json
ok=true
```
