#!/usr/bin/env python3
import json
import time
from pathlib import Path

import pandas as pd


SRC_OUT = Path("/root/gsm8k_single_language_experiment/swh_Latn")
DST_OUT = Path("/root/gsm8k_single_language_experiment/npi_Deva")
REWRITE_DIR = DST_OUT / "rewrites_en"
OUT_PATH = REWRITE_DIR / "english_rewrite_records.jsonl"
META_PATH = REWRITE_DIR / "reused_english_rewrite_meta.json"
PROGRESS_PATH = Path("/root/gsm8k_nepali_sid_worklog.md")


def now_utc() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> None:
    REWRITE_DIR.mkdir(parents=True, exist_ok=True)

    paths = []
    default_path = SRC_OUT / "rewrites_en" / "english_rewrite_records.jsonl"
    if default_path.exists():
        paths.append(default_path)
    paths.extend(sorted((SRC_OUT / "rewrites_en").glob("english_rewrite_records_rank*_of_*.jsonl")))

    english = {}
    seen_rows = 0
    bad_rows = 0
    for path in paths:
        for rec in read_jsonl(path):
            seen_rows += 1
            if rec.get("status") == "ok" and len(rec.get("rewrites") or []) == 5:
                english[(str(rec["split"]), int(rec["source_idx"]))] = rec
            else:
                bad_rows += 1

    target_df = pd.read_parquet(DST_OUT / "source.parquet")
    target_lookup = {
        (str(row["split"]), int(row["source_idx"])): row
        for row in target_df.to_dict("records")
    }
    missing = [key for key in target_lookup if key not in english]
    if missing:
        raise RuntimeError(f"missing {len(missing)} English rewrite keys, first={missing[:5]}")

    created_at = now_utc()
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for row in target_df.to_dict("records"):
            key = (str(row["split"]), int(row["source_idx"]))
            rec = dict(english[key])
            rec.update(
                {
                    "status": "ok",
                    "error": None,
                    "split": key[0],
                    "source_idx": key[1],
                    "target_question": str(row["question"]),
                    "answer": str(row["answer"]),
                    "target": row.get("target"),
                    "lang": "npi_Deva",
                    "created_at": created_at,
                    "reused_english_rewrites_from": str(SRC_OUT),
                }
            )
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    meta = {
        "created_at": created_at,
        "lang": "npi_Deva",
        "lang_name": "Nepali",
        "reason": (
            "English rewrite stage is target-language independent; reused complete "
            "gpt-oss English rewrites from swh_Latn and replaced target-language "
            "fields from npi_Deva source.parquet."
        ),
        "source_experiment": str(SRC_OUT),
        "source_paths": [str(path) for path in paths],
        "source_rows_seen": seen_rows,
        "source_bad_rows_ignored": bad_rows,
        "unique_ok_english_records": len(english),
        "target_records": len(target_df),
        "output": str(OUT_PATH),
    }
    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, sort_keys=True)

    with PROGRESS_PATH.open("a", encoding="utf-8") as f:
        f.write(f"\n## Update {created_at}\n\n")
        f.write("- Reused complete target-independent English rewrite records for `npi_Deva` from `swh_Latn`.\n")
        f.write(
            f"- Unique OK English rewrite records: `{len(english)}`; target records: `{len(target_df)}`; "
            f"source bad rows ignored: `{bad_rows}`.\n"
        )
        f.write(f"- Wrote `{OUT_PATH}` and `{META_PATH}`.\n")

    print(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
