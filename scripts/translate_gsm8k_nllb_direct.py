#!/usr/bin/env python3
"""Directly translate GSM8K parquet files with NLLB-200.

Output layout mirrors the input dataset:

  /root/gsm8k_nllb_direct/<lang>/main/train-00000-of-00001.parquet
  /root/gsm8k_nllb_direct/<lang>/main/test-00000-of-00001.parquet
  /root/gsm8k_nllb_direct/<lang>/socratic/...

Each parquet keeps the original columns: question, answer.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import time
from pathlib import Path


def hide_broken_optional_torch_packages() -> None:
    blocked = ("torchvision", "torchaudio")
    real_find_spec = importlib.util.find_spec

    def patched_find_spec(name: str, *args, **kwargs):
        if name in blocked or any(name.startswith(f"{pkg}.") for pkg in blocked):
            return None
        return real_find_spec(name, *args, **kwargs)

    importlib.util.find_spec = patched_find_spec


hide_broken_optional_torch_packages()

import pandas as pd
import torch
from tqdm.auto import tqdm
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


DEFAULT_LANGUAGES = [
    "swh_Latn",
    "yor_Latn",
    "amh_Ethi",
    "hau_Latn",
    "ibo_Latn",
    "som_Latn",
    "npi_Deva",
    "sin_Sinh",
    "khm_Khmr",
    "lao_Laoo",
    "mya_Mymr",
    "zul_Latn",
]

LANGUAGE_NAMES = {
    "swh_Latn": "Swahili",
    "yor_Latn": "Yoruba",
    "amh_Ethi": "Amharic",
    "hau_Latn": "Hausa",
    "ibo_Latn": "Igbo",
    "som_Latn": "Somali",
    "npi_Deva": "Nepali",
    "sin_Sinh": "Sinhala",
    "khm_Khmr": "Khmer",
    "lao_Laoo": "Lao",
    "mya_Mymr": "Burmese",
    "zul_Latn": "Zulu",
}

PROTECTED_LINE_RE = re.compile(r"^\s*####\s*[-+]?\d[\d,]*(?:\.\d+)?\s*$")
PROTECTED_TOKEN_RE = re.compile(
    r"<<[^>\n]*>>"  # GSM8K calculator annotation
    r"|\*\*"  # Socratic separator
    r"|\$?\d[\d,]*(?:\.\d+)?(?:/\d+)?%?"  # numbers, money, simple fractions
)


def key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_keep_newlines(text: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    for line in str(text).splitlines(keepends=True):
        if line.endswith("\r\n"):
            parts.append((line[:-2], "\r\n"))
        elif line.endswith("\n"):
            parts.append((line[:-1], "\n"))
        elif line.endswith("\r"):
            parts.append((line[:-1], "\r"))
        else:
            parts.append((line, ""))
    if not parts and text == "":
        parts.append(("", ""))
    return parts


def translatable_units(text: str) -> list[str]:
    units: list[str] = []
    for line, _newline in split_keep_newlines(str(text)):
        if not line.strip():
            continue
        if PROTECTED_LINE_RE.match(line):
            continue
        units.append(mask_line(line)[0])
    return units


def mask_line(line: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"[P{len(protected) - 1}]"

    return PROTECTED_TOKEN_RE.sub(replace, line), protected


def restore_line(translated: str, protected: list[str]) -> str:
    restored = translated
    for index, value in enumerate(protected):
        restored, count = re.subn(rf"\[\s*P\s*{index}\s*\]", value, restored, count=1, flags=re.IGNORECASE)
        if count == 0:
            # If NLLB drops a placeholder, keep the original token at the end
            # rather than losing GSM8K's numeric/annotation payload.
            restored = f"{restored} {value}"
    restored = re.sub(r"\[\s*P\s*\d+\s*\]", "", restored, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", restored).strip()


def reconstruct_text(text: str, cache: dict[str, str]) -> str:
    pieces: list[str] = []
    for line, newline in split_keep_newlines(str(text)):
        if not line.strip() or PROTECTED_LINE_RE.match(line):
            pieces.append(line + newline)
        else:
            masked, protected = mask_line(line)
            pieces.append(restore_line(cache[key(masked)], protected) + newline)
    return "".join(pieces)


def load_cache(path: Path) -> dict[str, str]:
    cache: dict[str, str] = {}
    if not path.exists():
        return cache
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                cache[row["key"]] = row["translation"]
    return cache


def append_cache(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def input_files(input_dir: Path) -> list[Path]:
    files = []
    for config in ("main", "socratic"):
        for split in ("train", "test"):
            files.extend(sorted((input_dir / config).glob(f"{split}-*.parquet")))
    if len(files) != 4:
        raise FileNotFoundError(f"expected 4 parquet files under {input_dir}, found {len(files)}")
    return files


def collect_texts(files: list[Path]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for path in files:
        df = pd.read_parquet(path)
        for row in df.itertuples(index=False):
            for value in (row.question, row.answer):
                for unit in translatable_units(value):
                    texts.setdefault(key(unit), unit)
    return texts


def translate_missing(
    model,
    tokenizer,
    missing: list[tuple[str, str]],
    target_lang: str,
    cache_path: Path,
    cache: dict[str, str],
    batch_size: int,
    source_max_length: int,
    target_max_length: int,
    device: str,
) -> None:
    forced_bos_token_id = tokenizer.convert_tokens_to_ids(target_lang)
    if forced_bos_token_id is None or forced_bos_token_id < 0:
        raise ValueError(f"NLLB language code not found: {target_lang}")

    for offset in tqdm(range(0, len(missing), batch_size), desc=target_lang, unit="batch"):
        chunk = missing[offset : offset + batch_size]
        batch = [text for _k, text in chunk]
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=source_max_length,
        ).to(device)
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=target_max_length,
                num_beams=1,
            )
        translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        rows = []
        for (text_key, source), translation in zip(chunk, translations):
            translation = translation.strip()
            cache[text_key] = translation
            rows.append(
                {
                    "key": text_key,
                    "source": source,
                    "translation": translation,
                    "target_lang": target_lang,
                }
            )
        append_cache(cache_path, rows)


def write_language_outputs(files: list[Path], input_dir: Path, output_dir: Path, target_lang: str, cache: dict[str, str]) -> None:
    for path in files:
        rel = path.relative_to(input_dir)
        out_path = output_dir / target_lang / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.read_parquet(path)
        out = df.copy()
        out["question"] = out["question"].astype(str).map(lambda x: reconstruct_text(x, cache))
        out["answer"] = out["answer"].astype(str).map(lambda x: reconstruct_text(x, cache))
        tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
        out.to_parquet(tmp_path, index=False)
        tmp_path.replace(out_path)
        print(f"wrote {out_path} rows={len(out)}", flush=True)


def write_metadata(input_dir: Path, output_dir: Path, languages: list[str], model_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source": str(input_dir),
        "model": str(model_dir),
        "source_language": "eng_Latn",
        "languages": [{"code": code, "name": LANGUAGE_NAMES.get(code, code)} for code in languages],
        "generated_at_unix": int(time.time()),
        "layout": "<output>/<lang>/{main,socratic}/{train,test}-*.parquet",
        "columns": ["question", "answer"],
    }
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    for name in ("README.md", "eval.yaml", ".gitattributes"):
        src = input_dir / name
        if src.exists():
            shutil.copy2(src, output_dir / name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("/root/gsm8k"))
    parser.add_argument("--output", type=Path, default=Path("/root/gsm8k_nllb_direct"))
    parser.add_argument("--model", type=Path, default=Path("/root/nllb-200-1.3B"))
    parser.add_argument("--languages", nargs="+", default=DEFAULT_LANGUAGES)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--source-max-length", type=int, default=512)
    parser.add_argument("--target-max-length", type=int, default=512)
    parser.add_argument("--max-length", type=int, default=None, help="backward-compatible alias for both source and target max length")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--limit-texts", type=int, default=0, help="smoke test: translate only first N texts and do not write parquet")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_length is not None:
        args.source_max_length = args.max_length
        args.target_max_length = args.max_length
    if args.device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        try:
            torch.backends.cuda.enable_cudnn_sdp(False)
        except Exception:
            pass

    files = input_files(args.input)
    texts = collect_texts(files)
    print(f"files={len(files)} unique_texts={len(texts)} languages={len(args.languages)}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model, src_lang="eng_Latn")
    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.model,
        dtype=torch.float16 if args.device == "cuda" else torch.float32,
        attn_implementation="eager",
    ).to(args.device)
    model.eval()

    for lang in args.languages:
        cache_path = args.output / ".cache" / f"eng_Latn__{lang}.jsonl"
        cache = load_cache(cache_path)
        missing = [(text_key, text) for text_key, text in texts.items() if text_key not in cache]
        if args.limit_texts:
            missing = missing[: args.limit_texts]
        print(f"{lang}: cached={len(cache)} missing={len(missing)}", flush=True)
        translate_missing(
            model=model,
            tokenizer=tokenizer,
            missing=missing,
            target_lang=lang,
            cache_path=cache_path,
            cache=cache,
            batch_size=args.batch_size,
            source_max_length=args.source_max_length,
            target_max_length=args.target_max_length,
            device=args.device,
        )
        if args.limit_texts:
            print(f"{lang}: smoke mode, not writing parquet", flush=True)
            continue
        write_language_outputs(files, args.input, args.output, lang, cache)

    if not args.limit_texts:
        write_metadata(args.input, args.output, args.languages, args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
