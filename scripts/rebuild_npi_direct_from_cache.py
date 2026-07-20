#!/usr/bin/env python3
import json
import shutil
import time
from pathlib import Path

import translate_gsm8k_nllb_direct as nllb


INPUT_DIR = Path("/root/gsm8k")
OUTPUT_DIR = Path("/root/gsm8k_nllb_direct")
LANG = "npi_Deva"
WORKLOG_PATH = Path("/root/gsm8k_nepali_sid_worklog.md")


def now_utc() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())


def main() -> None:
    files = nllb.input_files(INPUT_DIR)
    texts = nllb.collect_texts(files)
    cache_path = OUTPUT_DIR / ".cache" / f"eng_Latn__{LANG}.jsonl"
    cache = nllb.load_cache(cache_path)
    missing = [text_key for text_key in texts if text_key not in cache]
    if missing:
        raise RuntimeError(f"cache is missing {len(missing)} source texts; first={missing[:5]}")

    old_dir = OUTPUT_DIR / LANG
    backup_dir = OUTPUT_DIR / f"{LANG}.backup_before_placeholder_fix_{int(time.time())}"
    if old_dir.exists():
        shutil.copytree(old_dir, backup_dir)

    nllb.write_language_outputs(files, INPUT_DIR, OUTPUT_DIR, LANG, cache)
    nllb.write_metadata(INPUT_DIR, OUTPUT_DIR, [LANG], Path("/root/nllb-200-1.3B"))

    meta = {
        "created_at": now_utc(),
        "lang": LANG,
        "cache_path": str(cache_path),
        "cache_rows": len(cache),
        "unique_source_texts": len(texts),
        "backup_dir": str(backup_dir) if old_dir.exists() else None,
        "output_dir": str(old_dir),
        "reason": "Rebuilt with placeholder restoration that recognizes Devanagari placeholder digits such as [P०].",
    }
    meta_path = OUTPUT_DIR / f"{LANG}_placeholder_fix_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with WORKLOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"\n## Update {meta['created_at']}\n\n")
        f.write("- Rebuilt `/root/gsm8k_nllb_direct/npi_Deva` from the existing NLLB cache after fixing placeholder restoration.\n")
        f.write(f"- Cache rows: `{len(cache)}`; unique source texts required: `{len(texts)}`; missing: `0`.\n")
        if meta["backup_dir"]:
            f.write(f"- Backed up the previous direct translation directory to `{meta['backup_dir']}`.\n")
        f.write(f"- Wrote rebuild metadata to `{meta_path}`.\n")

    print(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
