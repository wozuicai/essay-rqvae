#!/usr/bin/env bash
set -euo pipefail

PY=/mnt/bn/search-gec-agentic-search-useast1b/guo/venvs/MiniOneRec-B200-moe/bin/python
SCRIPT=/root/run_gsm8k_single_language_experiment.py
OUT=/root/gsm8k_single_language_experiment/swh_Latn
LOGDIR=$OUT/eval/logs

mkdir -p "$LOGDIR"

for r in 0 1 2 3 4 5 6 7; do
  (
    cd /root
    export CUDA_VISIBLE_DEVICES=$r
    export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
    "$PY" "$SCRIPT" eval-generate \
      --lang swh_Latn \
      --lang-name Swahili \
      --out-dir "$OUT" \
      --qwen-model /root/qwen3.5-9B-instruct \
      --rank "$r" \
      --world-size 8 \
      --batch-size 8 \
      --max-input-length 2048 \
      --max-new-tokens 256 \
      --overwrite
  ) > "$LOGDIR/eval_rank${r}.log" 2>&1 &
done

wait
