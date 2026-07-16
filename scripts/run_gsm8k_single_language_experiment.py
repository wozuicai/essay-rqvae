#!/usr/bin/env python3
import argparse
import dataclasses
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


DEFAULT_LANG = "swh_Latn"
DEFAULT_LANG_NAME = "Swahili"
DEFAULT_SOURCE_DIR = Path("/root/gsm8k_nllb_direct")
DEFAULT_OUT_DIR = Path("/root/gsm8k_single_language_experiment") / DEFAULT_LANG
DEFAULT_REWRITE_MODEL = Path("/mnt/bn/search-gec-agentic-search-useast1b/guo/gpt-oss-120B")
DEFAULT_QWEN_MODEL = Path("/root/qwen3.5-9B-instruct")
DEFAULT_PROGRESS = Path("/root/gsm8k_query_rewrite_rqvae_worklog.md")


def now_utc() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def append_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()


def write_json(path: Path, obj: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_progress(message: str, progress_path: Path = DEFAULT_PROGRESS) -> None:
    stamp = now_utc()
    with progress_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## Update {stamp}\n\n{message.rstrip()}\n")


def normalize_number_text(text: str) -> Optional[str]:
    if text is None:
        return None
    s = str(text)
    s = s.replace(",", "")
    s = s.replace("$", "")
    s = s.strip()
    frac = re.search(r"-?\d+\s*/\s*-?\d+", s)
    if frac:
        a, b = frac.group(0).split("/")
        try:
            return str(float(a.strip()) / float(b.strip()))
        except Exception:
            return frac.group(0).replace(" ", "")
    nums = re.findall(r"-?\d+(?:\.\d+)?", s)
    if not nums:
        return None
    val = nums[-1]
    if "." in val:
        val = val.rstrip("0").rstrip(".")
    return val


def parse_target(answer: str) -> Optional[str]:
    if answer is None:
        return None
    text = str(answer)
    m = re.search(r"####\s*([^\n\r]+)", text)
    if m:
        return normalize_number_text(m.group(1))
    return normalize_number_text(text)


def extract_prediction(text: str) -> Optional[str]:
    if not text:
        return None
    candidates = []
    for pat in [
        r"####\s*([^\n\r]+)",
        r"\\boxed\{([^}]+)\}",
        r"final answer is[:\s]*([^\n\r]+)",
        r"answer is[:\s]*([^\n\r]+)",
    ]:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            candidates.append(m.group(1))
    if candidates:
        return normalize_number_text(candidates[-1])
    return None


def extract_relaxed_prediction(text: str) -> Optional[str]:
    if not text:
        return None
    cleaned = str(text).replace(",", "").replace("$", "")
    number_pattern = r"-?\d+(?:\.\d+)?\s*/\s*-?\d+(?:\.\d+)?|-?\d+(?:\.\d+)?"
    matches = re.findall(number_pattern, cleaned)
    if not matches:
        return None
    return normalize_number_text(matches[-1])


def numbers_equal(pred: Optional[str], target: Optional[str]) -> bool:
    if pred is None or target is None:
        return False
    try:
        return abs(float(pred) - float(target)) <= 1e-6
    except Exception:
        return pred.strip() == target.strip()


def source_path(source_dir: Path, lang: str, split: str) -> Path:
    return source_dir / lang / "main" / f"{split}-00000-of-00001.parquet"


def cmd_prepare(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)
    records: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {}
    for split in ["train", "test"]:
        path = source_path(Path(args.source_dir), args.lang, split)
        df = pd.read_parquet(path)
        counts[split] = int(len(df))
        for i, row in df.reset_index(drop=True).iterrows():
            records.append(
                {
                    "split": split,
                    "source_idx": int(i),
                    "question": str(row["question"]),
                    "answer": str(row["answer"]),
                    "target": parse_target(str(row["answer"])),
                }
            )
    source_df = pd.DataFrame(records)
    source_df.to_parquet(out_dir / "source.parquet", index=False)
    append_jsonl(out_dir / "source.jsonl", source_df.to_dict("records"))
    meta = {
        "created_at": now_utc(),
        "lang": args.lang,
        "lang_name": args.lang_name,
        "source_dir": str(args.source_dir),
        "counts": counts,
        "total": int(len(source_df)),
        "outputs": {
            "source_parquet": str(out_dir / "source.parquet"),
            "source_jsonl": str(out_dir / "source.jsonl"),
        },
    }
    write_json(out_dir / "prepare_meta.json", meta)
    append_progress(
        f"- Prepared `{args.lang}` source data under `{out_dir}`.\n"
        f"- Counts: train `{counts.get('train')}`, test `{counts.get('test')}`, total `{len(source_df)}`.\n"
        f"- Wrote `source.parquet`, `source.jsonl`, and `prepare_meta.json`."
    )


def language_native_name(lang: str, lang_name: str) -> str:
    if lang == "swh_Latn":
        return "Kiswahili"
    if lang == "amh_Ethi":
        return "አማርኛ"
    if lang == "npi_Deva":
        return "नेपाली"
    if lang == "hau_Latn":
        return "Hausa"
    return lang_name


def language_requirement(lang: str, lang_name: str) -> str:
    native = language_native_name(lang, lang_name)
    if lang == "amh_Ethi":
        return (
            "Every rewrite must be in Amharic using Ethiopic script. "
            "Do not use English sentences. "
        )
    if lang == "npi_Deva":
        return (
            "Every rewrite must be in Nepali using Devanagari script. "
            "Do not use English sentences. "
        )
    if lang == "hau_Latn":
        return (
            "Every rewrite must be in Hausa. "
            "Do not use English sentences. "
        )
    if lang == "swh_Latn":
        return "Every rewrite must be in standard Swahili. "
    return f"Every rewrite must stay in {lang_name}. "


def make_rewrite_messages(question: str, lang: str, lang_name: str) -> List[Dict[str, str]]:
    native = language_native_name(lang, lang_name)
    requirement = language_requirement(lang, lang_name)
    if lang == "npi_Deva":
        system = (
            "Reasoning: low\n"
            "You are a careful editor of Nepali grade-school math questions. "
            "Every rewrite must be in Nepali using Devanagari script. "
            "Preserve the exact meaning, names, currency symbols, and all numbers. "
            "Do not solve the problem. Return only one strict JSON object."
        )
        user = (
            "Language: Nepali (npi_Deva)\n\n"
            "Original question:\n"
            f"{question}\n\n"
            "Write exactly 5 substantially different Nepali rewrites. "
            "All rewrites must use Devanagari script. Keep all numbers and names unchanged. "
            "Do not add hints and do not solve.\n\n"
            "Use this JSON shape only:\n"
            '{"rewrites":["सीताले सोमबार 12 कलम र मंगलबार 6 कलम किनिन्। उनले जम्मा कति कलम किनिन्?",'
            '"सोमबार 12 र मंगलबार 6 कलम किनेपछि सीतासँग कति कलम भए?",'
            '"सीताले पहिले 12 कलम किनिन् र अर्को दिन 6 कलम थपिन्। कुल कलमको संख्या कति भयो?",'
            '"यदि सीताले एक दिन 12 कलम र अर्को दिन 6 कलम किनेकी छिन् भने, उनले सबै गरेर कति कलम किनेकी छिन्?",'
            '"दुई दिनमा 12 र 6 कलम किनेकी सीताले जम्मा कति कलम किनेकी हो?"]}\n\n'
            'Return JSON with the key "rewrites" only.'
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    if lang == "hau_Latn":
        system = (
            "Reasoning: low\n"
            "Kai kwararren edita ne na tambayoyin lissafi cikin Hausa. "
            "Ka adana ma'ana, sunaye, alamar kudi, da dukkan lambobi. "
            "Kada ka warware tambayar. Ka mayar da JSON daya kacal."
        )
        user = (
            "Harshe: Hausa (hau_Latn)\n\n"
            "Tambaya ta asali:\n"
            f"{question}\n\n"
            "A sake rubuta wannan tambaya sau 5 cikin Hausa mai kyau. "
            "Kowace siga ta bambanta da sauran wajen tsari da kalmomi, amma ma'anar ta kasance iri daya. "
            "A bar dukkan lambobi da sunaye kamar yadda suke. Kada a bayar da amsa. "
            "Yi amfani da kalmomin Hausa kamar 'awa daya', 'minti', 'rabin', 'jimilla', 'watan', "
            "'kula da yara', 'ta samu', da 'ta sayar'. Kada a rubuta kalmomin Turanci a cikin sigogin.\n\n"
            "Misalin tsarin JSON:\n"
            '{"rewrites":["Aisha ta sayi alkaluma 12 ranar Litinin da alkaluma 6 ranar Talata. Alkaluma nawa ta saya gaba daya?",'
            '"Ranar Litinin Aisha ta samu alkaluma 12, sannan ranar Talata ta kara 6. Yawan alkaluman ya zama nawa?",'
            '"Idan Aisha ta sayi alkaluma 12 a rana daya, sannan ta sayi 6 a rana ta gaba, alkaluma nawa ta saya gaba daya?",'
            '"Aisha tana da sayayyar alkaluma 12 ranar Litinin da 6 ranar Talata. Jimillar alkaluman nawa ne?",'
            '"Bayan Aisha ta sayi alkaluma 12 da kuma 6 a kwanaki biyu, alkaluma nawa ta saya baki daya?"]}\n\n'
            'Ka mayar da JSON mai mabudin "rewrites" kadai.'
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    system = (
        "Reasoning: low\n"
        f"You are an editor of grade-school math questions in {native}. "
        f"{requirement}"
        "Hifadhi maana, majina, alama za fedha, na namba zote. "
        "Usihesabu jibu. Rudisha JSON moja tu."
    )
    user = (
        f"Lugha: {native} ({lang_name}, {lang})\n\n"
        "Swali la awali:\n"
        f"{question}\n\n"
        f"Kazi: andika upya swali hili mara 5 kwa {native}. "
        "Kila toleo libadili mpangilio na maneno, lakini maana ibaki ileile. "
        "Namba zote na majina yote yabaki kama yalivyo. Usitoe suluhisho.\n\n"
        "Mfano wa mtindo unaotakiwa:\n"
        '{"rewrites":["Asha alinunua kalamu 12 Jumatatu na kalamu 6 Jumanne. Kwa siku hizo mbili alinunua kalamu ngapi?",'
        '"Jumatatu Asha alipata kalamu 12, kisha Jumanne akapata kalamu 6. Jumla ya kalamu alizopata ni ipi?",'
        '"Ikiwa Asha alinunua kalamu 12 siku ya Jumatatu na 6 siku ya Jumanne, alikuwa na kalamu ngapi kwa pamoja?",'
        '"Asha alikuwa na manunuzi ya kalamu 12 Jumatatu na 6 Jumanne. Idadi yote ya kalamu ni kiasi gani?",'
        '"Baada ya kununua kalamu 12 Jumatatu na 6 Jumanne, Asha alinunua kalamu ngapi kwa ujumla?"]}\n\n'
        'Rudisha JSON yenye ufunguo "rewrites" pekee.'
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def make_rewrite_prompt(question: str, lang: str, lang_name: str) -> str:
    messages = make_rewrite_messages(question, lang, lang_name)
    system = messages[0]["content"]
    user = messages[1]["content"]
    return (
        "<|start|>system<|message|>"
        "You are ChatGPT, a large language model trained by OpenAI.\n"
        "Reasoning: low\n\n"
        "# Valid channels: final. Channel must be included for every message.\n"
        f"{system}"
        "<|end|>"
        "<|start|>user<|message|>"
        f"{user}"
        "<|end|>"
        "<|start|>assistant<|channel|>final<|message|>"
    )


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_json_candidate(text: str) -> str:
    text = strip_code_fence(text)
    text = text.replace("\u202f", " ").replace("\u00a0", " ")
    marker = "assistantfinal"
    marker_pos = text.rfind(marker)
    if marker_pos >= 0:
        text = text[marker_pos + len(marker) :].strip()
    text = re.sub(r"^(?:JSON|json)\s*", "", text.strip())
    if text.startswith("{") or text.startswith("["):
        return text
    obj_start = text.find("{")
    obj_end = text.rfind("}")
    if obj_start >= 0 and obj_end > obj_start:
        return text[obj_start : obj_end + 1]
    arr_start = text.find("[")
    arr_end = text.rfind("]")
    if arr_start >= 0 and arr_end > arr_start:
        return text[arr_start : arr_end + 1]
    return text


ENGLISH_LEAK_RE = re.compile(
    r"\b(?:the|and|or|for|per|hour|yesterday|how|much|did|earn|receive|receives|"
    r"spent|babysitting|only|paid|total|sell|sold|with|from|what|is|she|he)\b",
    flags=re.IGNORECASE,
)


def extract_number_tokens(text: str) -> List[str]:
    return re.findall(r"\$?\d+(?:,\d{3})*(?:\.\d+)?", text or "")


def normalize_rewrite_key(key: str) -> str:
    return re.sub(r"[^A-Za-z_]", "", key or "").lower()


def validate_rewrite_language(rewrites: Sequence[str], lang: str) -> Optional[str]:
    if lang == "hau_Latn":
        english_word = re.compile(
            r"\b(?:the|and|or|for|per|hour|yesterday|how|much|did|earn|receive|"
            r"receives|spent|babysitting|only|paid|total|sell|sold|with|from|"
            r"what|is|she|he|does|get|gets|doing|minutes|question|answer|"
            r"april|may|half|clips|month|child|children|care)\b",
            flags=re.IGNORECASE,
        )
        hausa_hint = re.compile(
            r"\b(?:da|ta|ya|a|watan|rabin|jimillar|gaba|daya|nawa|samu|sayi|"
            r"sayar|yara|kula|minti|awa)\b",
            flags=re.IGNORECASE,
        )
        for i, rewrite in enumerate(rewrites):
            match = english_word.search(rewrite)
            if match:
                return f"rewrite {i} contains likely English word: {match.group(0)}"
            if not hausa_hint.search(rewrite):
                return f"rewrite {i} lacks common Hausa markers"
        return None
    if lang == "npi_Deva":
        devanagari = re.compile(r"[\u0900-\u097F]")
        latin_word = re.compile(
            r"\b(?:the|and|or|for|per|hour|yesterday|how|much|did|earn|receive|"
            r"receives|spent|babysitting|only|paid|total|sell|sold|with|from|"
            r"what|is|she|he|does|get|gets|doing|minutes|question|answer)\b",
            flags=re.IGNORECASE,
        )
        for i, rewrite in enumerate(rewrites):
            if not devanagari.search(rewrite):
                return f"rewrite {i} lacks Devanagari script"
            match = latin_word.search(rewrite)
            if match:
                return f"rewrite {i} contains likely English word: {match.group(0)}"
        return None
    if lang == "amh_Ethi":
        ethiopic = re.compile(r"[\u1200-\u137F]")
        latin_word = re.compile(
            r"\b(?:the|and|or|for|per|hour|yesterday|how|much|did|earn|receive|"
            r"receives|spent|babysitting|only|paid|total|sell|sold|with|from|"
            r"what|is|she|he|does|get|gets|doing|minutes)\b",
            flags=re.IGNORECASE,
        )
        for i, rewrite in enumerate(rewrites):
            if not ethiopic.search(rewrite):
                return f"rewrite {i} lacks Ethiopic script"
            match = latin_word.search(rewrite)
            if match:
                return f"rewrite {i} contains likely English word: {match.group(0)}"
        return None
    if lang != "swh_Latn":
        return None
    for i, rewrite in enumerate(rewrites):
        match = ENGLISH_LEAK_RE.search(rewrite)
        if match:
            return f"rewrite {i} contains likely English word: {match.group(0)}"
    return None


def validate_rewrite_numbers(rewrites: Sequence[str], original: str) -> Optional[str]:
    original_numbers = extract_number_tokens(original)
    if not original_numbers:
        return None
    for i, rewrite in enumerate(rewrites):
        for num in original_numbers:
            if num not in rewrite:
                return f"rewrite {i} missing original number: {num}"
    return None


def parse_rewrites(raw: str, original: str, expected: int = 5) -> Tuple[List[str], Optional[str]]:
    try:
        obj = json.loads(extract_json_candidate(raw))
        if isinstance(obj, dict):
            vals = obj.get("rewrites")
            if vals is None:
                for key, value in obj.items():
                    if normalize_rewrite_key(str(key)).endswith("rewrites"):
                        vals = value
                        break
        else:
            vals = obj
        if not isinstance(vals, list):
            return [], "json did not contain a list"
        rewrites: List[str] = []
        seen = set()
        for val in vals:
            if not isinstance(val, str):
                continue
            s = " ".join(val.strip().split())
            if not s:
                continue
            key = s.casefold()
            if key in seen:
                continue
            seen.add(key)
            rewrites.append(s)
        if len(rewrites) != expected:
            return rewrites, f"expected {expected}, got {len(rewrites)}"
        if any(r == original for r in rewrites):
            return rewrites, "one rewrite exactly equals original"
        number_err = validate_rewrite_numbers(rewrites, original)
        if number_err is not None:
            return rewrites, number_err
        return rewrites, None
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"


def patch_vllm_tokenizer_cache_for_transformers5() -> None:
    """Patch vLLM's tokenizer cache for transformers tokenizers missing one HF property.

    The local gpt-oss tokenizer loads as a Transformers 5 tokenizer backend that has
    all_special_tokens but not all_special_tokens_extended. vLLM 0.10.1 reads the
    latter unconditionally while creating its cached tokenizer proxy. Keep this patch
    process-local so the shared venv package is not modified.
    """
    import contextlib
    import copy

    import vllm.transformers_utils.tokenizer as vllm_tokenizer

    def get_cached_tokenizer_compat(tokenizer: Any) -> Any:
        cached_tokenizer = copy.copy(tokenizer)
        tokenizer_all_special_ids = tokenizer.all_special_ids
        tokenizer_all_special_tokens = tokenizer.all_special_tokens
        tokenizer_all_special_tokens_extended = getattr(
            tokenizer,
            "all_special_tokens_extended",
            tokenizer_all_special_tokens,
        )
        tokenizer_vocab = tokenizer.get_vocab()
        tokenizer_len = len(tokenizer)

        max_token_id = max(tokenizer_vocab.values())
        if hasattr(tokenizer, "vocab_size"):
            with contextlib.suppress(NotImplementedError):
                max_token_id = max(max_token_id, tokenizer.vocab_size)

        class CachedTokenizer(tokenizer.__class__):  # type: ignore
            @property
            def all_special_ids(self) -> List[int]:
                return tokenizer_all_special_ids

            @property
            def all_special_tokens(self) -> List[str]:
                return tokenizer_all_special_tokens

            @property
            def all_special_tokens_extended(self) -> List[str]:
                return tokenizer_all_special_tokens_extended

            @property
            def max_token_id(self) -> int:
                return max_token_id

            def get_vocab(self) -> Dict[str, int]:
                return tokenizer_vocab

            def __len__(self) -> int:
                return tokenizer_len

            def __reduce__(self) -> Any:
                return get_cached_tokenizer_compat, (tokenizer,)

        CachedTokenizer.__name__ = f"Cached{tokenizer.__class__.__name__}"
        cached_tokenizer.__class__ = CachedTokenizer
        return cached_tokenizer

    vllm_tokenizer.get_cached_tokenizer = get_cached_tokenizer_compat


def load_completed_rewrites(path: Path) -> Dict[Tuple[str, int], Dict[str, Any]]:
    done: Dict[Tuple[str, int], Dict[str, Any]] = {}
    if not path.exists():
        return done
    for rec in read_jsonl(path):
        key = (str(rec.get("split")), int(rec.get("source_idx")))
        rewrites = rec.get("rewrites") or []
        if rec.get("status") == "ok" and len(rewrites) == 5:
            done[key] = rec
    return done


def english_rewrite_record_paths(out_dir: Path) -> List[Path]:
    rewrite_dir = out_dir / "rewrites_en"
    paths = []
    default_path = rewrite_dir / "english_rewrite_records.jsonl"
    if default_path.exists():
        paths.append(default_path)
    paths.extend(sorted(rewrite_dir.glob("english_rewrite_records_rank*_of_*.jsonl")))
    return paths


def load_completed_english_rewrites(out_dir: Path) -> Dict[Tuple[str, int], Dict[str, Any]]:
    done: Dict[Tuple[str, int], Dict[str, Any]] = {}
    for path in english_rewrite_record_paths(out_dir):
        for rec in read_jsonl(path):
            if rec.get("status") == "ok" and len(rec.get("rewrites") or []) == 5:
                done[(str(rec["split"]), int(rec["source_idx"]))] = rec
    return done


def load_key_filter(path: Optional[Path]) -> Optional[set]:
    if path is None:
        return None
    keys = set()
    for rec in read_jsonl(path):
        keys.add((str(rec["split"]), int(rec["source_idx"])))
    return keys


def cmd_rewrite(args: argparse.Namespace) -> None:
    patch_vllm_tokenizer_cache_for_transformers5()
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import GuidedDecodingParams

    out_dir = Path(args.out_dir)
    source_df = pd.read_parquet(out_dir / "source.parquet")
    records_path = out_dir / "rewrites" / "rewrite_records.jsonl"
    completed = load_completed_rewrites(records_path)
    pending_rows = []
    for row in source_df.to_dict("records"):
        key = (row["split"], int(row["source_idx"]))
        if key in completed:
            continue
        if args.split and row["split"] not in set(args.split):
            continue
        pending_rows.append(row)
    if args.limit:
        pending_rows = pending_rows[: args.limit]
    ensure_dir(records_path.parent)
    rewrite_meta = {
        "started_at": now_utc(),
        "model": str(args.rewrite_model),
        "lang": args.lang,
        "lang_name": args.lang_name,
        "already_completed": len(completed),
        "pending_this_run": len(pending_rows),
        "batch_size": args.batch_size,
        "tensor_parallel_size": args.tensor_parallel_size,
    }
    write_json(out_dir / "rewrites" / "rewrite_run_meta.json", rewrite_meta)
    append_progress(
        f"- Started rewrite stage for `{args.lang}` with gpt-oss model `{args.rewrite_model}`.\n"
        f"- Existing complete rewrite records: `{len(completed)}`; pending in this run: `{len(pending_rows)}`.\n"
        f"- Output file: `{records_path}`."
    )
    if not pending_rows:
        return

    llm_kwargs: Dict[str, Any] = {
        "model": str(args.rewrite_model),
        "trust_remote_code": True,
        "tensor_parallel_size": args.tensor_parallel_size,
        "gpu_memory_utilization": args.gpu_memory_utilization,
        "max_model_len": args.max_model_len,
        "enable_prefix_caching": True,
        "hf_overrides": {"rope_theta": args.rope_theta},
        "disable_custom_all_reduce": args.disable_custom_all_reduce,
        "enforce_eager": args.enforce_eager,
    }
    if args.max_num_seqs:
        llm_kwargs["max_num_seqs"] = args.max_num_seqs
    llm = LLM(**llm_kwargs)
    guided_decoding = None
    if args.guided_json:
        guided_kwargs: Dict[str, Any] = {}
        if args.guided_backend:
            guided_kwargs["backend"] = args.guided_backend
        guided_decoding = GuidedDecodingParams.from_optional(
            json={
                "type": "object",
                "additionalProperties": False,
                "required": ["rewrites"],
                "properties": {
                    "rewrites": {
                        "type": "array",
                        "minItems": 5,
                        "maxItems": 5,
                        "items": {"type": "string"},
                    }
                },
            },
            **guided_kwargs,
        )
    sampling = SamplingParams(
        n=args.num_candidates,
        temperature=args.temperature,
        top_p=args.top_p,
        presence_penalty=args.presence_penalty,
        frequency_penalty=args.frequency_penalty,
        repetition_penalty=args.repetition_penalty,
        max_tokens=args.max_tokens,
        guided_decoding=guided_decoding,
    )

    total_ok = 0
    total_bad = 0
    for start in range(0, len(pending_rows), args.batch_size):
        batch = pending_rows[start : start + args.batch_size]
        messages = [
            make_rewrite_messages(str(row["question"]), args.lang, args.lang_name) for row in batch
        ]
        outputs = llm.chat(
            messages,
            sampling_params=sampling,
            use_tqdm=False,
            chat_template_kwargs={"reasoning_effort": args.reasoning_effort},
        )
        out_records = []
        for row, out in zip(batch, outputs):
            candidate_results = []
            best_rewrites: List[str] = []
            best_raw = ""
            best_err: Optional[str] = "no outputs"
            best_candidate_idx = -1
            for candidate_idx, candidate in enumerate(out.outputs or []):
                raw = candidate.text
                rewrites, err = parse_rewrites(raw, str(row["question"]), expected=5)
                if err is None:
                    err = validate_rewrite_language(rewrites, args.lang)
                candidate_results.append(
                    {
                        "candidate_idx": candidate_idx,
                        "error": err,
                        "rewrites": rewrites,
                        "raw_output": raw,
                    }
                )
                if err is None:
                    best_rewrites = rewrites
                    best_raw = raw
                    best_err = None
                    best_candidate_idx = candidate_idx
                    break
                if best_candidate_idx < 0:
                    best_rewrites = rewrites
                    best_raw = raw
                    best_err = err
                    best_candidate_idx = candidate_idx
            raw = best_raw
            rewrites = best_rewrites
            err = best_err
            status = "ok" if err is None else "bad"
            if status == "ok":
                total_ok += 1
            else:
                total_bad += 1
            out_records.append(
                {
                    "status": status,
                    "error": err,
                    "split": row["split"],
                    "source_idx": int(row["source_idx"]),
                    "question": row["question"],
                    "answer": row["answer"],
                    "target": row.get("target"),
                    "rewrites": rewrites,
                    "raw_output": raw,
                    "candidate_idx": best_candidate_idx,
                    "candidate_results": candidate_results,
                    "model": str(args.rewrite_model),
                    "lang": args.lang,
                    "created_at": now_utc(),
                }
            )
        append_jsonl(records_path, out_records)
        print(
            f"rewrite progress {min(start + len(batch), len(pending_rows))}/{len(pending_rows)} "
            f"ok={total_ok} bad={total_bad}",
            flush=True,
        )
    append_progress(
        f"- Finished rewrite run for `{args.lang}`.\n"
        f"- This run parsed ok records: `{total_ok}`; bad records: `{total_bad}`.\n"
        f"- Rewrite records are in `{records_path}`."
    )


def cmd_build_variants(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    source_df = pd.read_parquet(out_dir / "source.parquet")
    records_path = out_dir / "rewrites" / "rewrite_records.jsonl"
    completed = load_completed_rewrites(records_path)
    rows: List[Dict[str, Any]] = []
    missing: List[Tuple[str, int]] = []
    for row in source_df.to_dict("records"):
        key = (row["split"], int(row["source_idx"]))
        rec = completed.get(key)
        if rec is None:
            missing.append(key)
            if not args.allow_incomplete:
                continue
            rewrites: List[str] = []
        else:
            rewrites = list(rec["rewrites"])
        variants = [row["question"]] + rewrites
        for variant_idx, question in enumerate(variants):
            rows.append(
                {
                    "variant_row": len(rows),
                    "variant_id": f"{row['split']}-{int(row['source_idx']):05d}-v{variant_idx}",
                    "split": row["split"],
                    "source_idx": int(row["source_idx"]),
                    "variant_idx": int(variant_idx),
                    "question": question,
                    "answer": row["answer"],
                    "target": row.get("target"),
                }
            )
    if missing and not args.allow_incomplete:
        raise RuntimeError(f"missing {len(missing)} complete rewrite records; rerun rewrite")
    variants_df = pd.DataFrame(rows)
    variants_dir = out_dir / "variants"
    ensure_dir(variants_dir)
    variants_df.to_parquet(variants_dir / "variants.parquet", index=False)
    for split in ["train", "test"]:
        variants_df[variants_df["split"] == split].to_parquet(
            variants_dir / f"{split}_variants.parquet", index=False
        )
    counts = variants_df.groupby(["split", "variant_idx"]).size().to_dict()
    meta = {
        "created_at": now_utc(),
        "num_rows": int(len(variants_df)),
        "missing_sources": len(missing),
        "counts_by_split_variant": {f"{k[0]}:v{k[1]}": int(v) for k, v in counts.items()},
        "variants_parquet": str(variants_dir / "variants.parquet"),
    }
    write_json(variants_dir / "variants_meta.json", meta)
    append_progress(
        f"- Built variant table for `{args.lang}`.\n"
        f"- Rows: `{len(variants_df)}`; missing source rewrite records: `{len(missing)}`.\n"
        f"- Output: `{variants_dir / 'variants.parquet'}`."
    )


def get_rank_world(args: argparse.Namespace) -> Tuple[int, int, int]:
    rank = int(os.environ.get("RANK", args.rank))
    world = int(os.environ.get("WORLD_SIZE", args.world_size))
    local_rank = int(os.environ.get("LOCAL_RANK", rank))
    return rank, world, local_rank


def tokenize_lengths(tokenizer: Any, texts: Sequence[str], max_length: int, batch_size: int) -> np.ndarray:
    lengths = np.zeros(len(texts), dtype=np.int32)
    for start in range(0, len(texts), batch_size):
        batch = list(texts[start : start + batch_size])
        enc = tokenizer(
            batch,
            add_special_tokens=True,
            truncation=True,
            max_length=max_length,
            padding=False,
        )
        lengths[start : start + len(batch)] = [len(x) for x in enc["input_ids"]]
    return lengths


def cmd_extract_hidden(args: argparse.Namespace) -> None:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    rank, world, local_rank = get_rank_world(args)
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank % torch.cuda.device_count())
        device = torch.device("cuda", local_rank % torch.cuda.device_count())
    else:
        device = torch.device("cpu")
    out_dir = Path(args.out_dir)
    variants_path = out_dir / "variants" / "variants.parquet"
    variants_df = pd.read_parquet(variants_path)
    all_indices = np.arange(len(variants_df), dtype=np.int64)
    shard_indices = all_indices[rank::world]
    if args.limit:
        shard_indices = shard_indices[: args.limit]
    hidden_dir = out_dir / "hidden"
    ensure_dir(hidden_dir)
    done_path = hidden_dir / f"shard_rank{rank:02d}_of_{world:02d}.done.json"
    if done_path.exists() and not args.overwrite:
        print(f"hidden shard already done: {done_path}")
        return
    tokenizer = AutoTokenizer.from_pretrained(str(args.qwen_model), trust_remote_code=True)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    texts = variants_df.loc[shard_indices, "question"].astype(str).tolist()
    lengths = tokenize_lengths(tokenizer, texts, args.max_length, args.length_batch_size)
    order = np.argsort(lengths, kind="stable")
    ordered_indices = shard_indices[order]
    ordered_lengths = lengths[order]

    model_kwargs = {
        "torch_dtype": torch.bfloat16,
        "trust_remote_code": True,
    }
    if args.attn_implementation:
        model_kwargs["attn_implementation"] = args.attn_implementation
    model = AutoModelForCausalLM.from_pretrained(str(args.qwen_model), **model_kwargs)
    model.to(device)
    model.eval()
    model.config.use_cache = False

    num_layers = int(model.config.num_hidden_layers) + 1
    hidden_size = int(model.config.hidden_size)
    tmp_path = hidden_dir / f"shard_rank{rank:02d}_of_{world:02d}.float16.memmap.partial"
    final_path = hidden_dir / f"shard_rank{rank:02d}_of_{world:02d}.float16.memmap"
    idx_path = hidden_dir / f"shard_rank{rank:02d}_of_{world:02d}.indices.npy"
    mmap = np.memmap(tmp_path, dtype=np.float16, mode="w+", shape=(len(ordered_indices), num_layers, hidden_size))

    write_json(
        hidden_dir / f"shard_rank{rank:02d}_of_{world:02d}.started.json",
        {
            "started_at": now_utc(),
            "rank": rank,
            "world": world,
            "local_rank": local_rank,
            "device": str(device),
            "num_rows": int(len(ordered_indices)),
            "num_layers": num_layers,
            "hidden_size": hidden_size,
            "batch_size": args.batch_size,
            "max_length": args.max_length,
            "qwen_model": str(args.qwen_model),
        },
    )
    append_progress(
        f"- Started hidden extraction shard rank `{rank}`/`{world}` for `{args.lang}`.\n"
        f"- Rows in shard: `{len(ordered_indices)}`; output temp: `{tmp_path}`."
    )

    pos = 0
    with torch.inference_mode():
        for start in range(0, len(ordered_indices), args.batch_size):
            rows = ordered_indices[start : start + args.batch_size]
            batch_texts = variants_df.loc[rows, "question"].astype(str).tolist()
            enc = tokenizer(
                batch_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=args.max_length,
                add_special_tokens=True,
            )
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc, output_hidden_states=True, use_cache=False)
            hs = out.hidden_states
            if len(hs) != num_layers:
                raise RuntimeError(f"expected {num_layers} hidden states, got {len(hs)}")
            stacked = torch.stack([h[:, -1, :].detach().to(torch.float16).cpu() for h in hs], dim=1)
            mmap[pos : pos + len(rows)] = stacked.numpy()
            mmap.flush()
            pos += len(rows)
            if pos % max(args.batch_size * 20, 1) == 0 or pos == len(ordered_indices):
                print(f"hidden rank {rank}/{world} {pos}/{len(ordered_indices)}", flush=True)
    np.save(idx_path, ordered_indices)
    np.save(hidden_dir / f"shard_rank{rank:02d}_of_{world:02d}.lengths.npy", ordered_lengths)
    del mmap
    os.replace(tmp_path, final_path)
    write_json(
        done_path,
        {
            "finished_at": now_utc(),
            "rank": rank,
            "world": world,
            "num_rows": int(len(ordered_indices)),
            "shape": [int(len(ordered_indices)), int(num_layers), int(hidden_size)],
            "indices": str(idx_path),
            "memmap": str(final_path),
        },
    )
    append_progress(
        f"- Finished hidden extraction shard rank `{rank}`/`{world}`.\n"
        f"- Shape: `{[int(len(ordered_indices)), int(num_layers), int(hidden_size)]}`; file: `{final_path}`."
    )


def cmd_merge_hidden(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    variants_df = pd.read_parquet(out_dir / "variants" / "variants.parquet")
    hidden_dir = out_dir / "hidden"
    done_files = sorted(hidden_dir.glob("shard_rank*_of_*.done.json"))
    if not done_files:
        raise RuntimeError(f"no hidden shard done files in {hidden_dir}")
    metas = [load_json(p) for p in done_files]
    num_layers = int(metas[0]["shape"][1])
    hidden_size = int(metas[0]["shape"][2])
    final_path = hidden_dir / "hidden_states.float16.memmap"
    final = np.memmap(final_path, dtype=np.float16, mode="w+", shape=(len(variants_df), num_layers, hidden_size))
    seen = np.zeros(len(variants_df), dtype=bool)
    for meta in metas:
        shape = tuple(meta["shape"])
        shard = np.memmap(meta["memmap"], dtype=np.float16, mode="r", shape=shape)
        indices = np.load(meta["indices"])
        for start in range(0, len(indices), args.chunk_size):
            end = min(start + args.chunk_size, len(indices))
            final[indices[start:end]] = shard[start:end]
            seen[indices[start:end]] = True
        final.flush()
    missing = np.where(~seen)[0].tolist()
    meta = {
        "created_at": now_utc(),
        "shape": [int(len(variants_df)), int(num_layers), int(hidden_size)],
        "dtype": "float16",
        "memmap": str(final_path),
        "num_shards": len(metas),
        "missing_rows": len(missing),
        "missing_preview": missing[:20],
    }
    write_json(hidden_dir / "hidden_states_meta.json", meta)
    append_progress(
        f"- Merged hidden-state shards for `{args.lang}`.\n"
        f"- Final shape: `{meta['shape']}`; missing rows: `{len(missing)}`; file: `{final_path}`."
    )
    if missing:
        raise RuntimeError(f"merged hidden states missing {len(missing)} rows")


class HiddenFlatDataset:
    def __init__(
        self,
        hidden_path: Path,
        shape: Sequence[int],
        variant_indices: np.ndarray,
        normalize: bool = True,
        layers: Optional[Sequence[int]] = None,
    ) -> None:
        self.hidden = np.memmap(hidden_path, dtype=np.float16, mode="r", shape=tuple(shape))
        self.variant_indices = np.asarray(variant_indices, dtype=np.int64)
        self.layers = np.asarray(list(range(shape[1])) if layers is None else list(layers), dtype=np.int64)
        self.normalize = normalize
        self.hidden_size = int(shape[2])

    def __len__(self) -> int:
        return int(len(self.variant_indices) * len(self.layers))

    def __getitem__(self, idx: int) -> Any:
        import torch

        row = self.variant_indices[idx // len(self.layers)]
        layer = self.layers[idx % len(self.layers)]
        x = np.asarray(self.hidden[row, layer], dtype=np.float32)
        if self.normalize:
            norm = np.linalg.norm(x)
            if norm > 1e-12:
                x = x / norm
        return torch.from_numpy(x)


def cmd_train_rqvae(args: argparse.Namespace) -> None:
    import torch
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, random_split

    sys.path.insert(0, "/root")
    from rqvae_title_pipeline import RQVAE, set_seed

    out_dir = Path(args.out_dir)
    variants_df = pd.read_parquet(out_dir / "variants" / "variants.parquet")
    hidden_meta = load_json(out_dir / "hidden" / "hidden_states_meta.json")
    hidden_path = Path(hidden_meta["memmap"])
    shape = hidden_meta["shape"]
    train_indices = variants_df.index[variants_df["split"] == "train"].to_numpy(dtype=np.int64)
    if args.limit_variants:
        train_indices = train_indices[: args.limit_variants]
    set_seed(args.seed)
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    dataset = HiddenFlatDataset(
        hidden_path=hidden_path,
        shape=shape,
        variant_indices=train_indices,
        normalize=not args.no_normalize,
    )
    n_val = max(1, int(len(dataset) * args.val_ratio)) if len(dataset) > 1 else 0
    n_train = len(dataset) - n_val
    if n_val:
        train_ds, val_ds = random_split(
            dataset,
            [n_train, n_val],
            generator=torch.Generator().manual_seed(args.seed),
        )
    else:
        train_ds, val_ds = dataset, dataset
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
    model = RQVAE(
        input_dim=int(shape[2]),
        latent_dim=args.latent_dim,
        num_codebooks=args.num_codebooks,
        codebook_size=args.codebook_size,
        beta_commit=args.beta_commit,
        ema_decay=args.ema_decay,
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    rqvae_dir = out_dir / "rqvae"
    ensure_dir(rqvae_dir)
    cfg = {
        "created_at": now_utc(),
        "hidden_shape": shape,
        "train_variant_count": int(len(train_indices)),
        "train_embedding_count": int(len(train_indices) * shape[1]),
        "normalize": not args.no_normalize,
        "latent_dim": args.latent_dim,
        "num_codebooks": args.num_codebooks,
        "codebook_size": args.codebook_size,
        "beta_commit": args.beta_commit,
        "ema_decay": args.ema_decay,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "seed": args.seed,
    }
    write_json(rqvae_dir / "train_config.json", cfg)
    append_progress(
        f"- Started RQVAE training for `{args.lang}`.\n"
        f"- Train variants: `{len(train_indices)}`; train embeddings: `{len(train_indices) * shape[1]}`.\n"
        f"- Config: codebook_size `{args.codebook_size}`, num_codebooks `{args.num_codebooks}`, latent_dim `{args.latent_dim}`."
    )
    history: List[Dict[str, Any]] = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_total = defaultdict(float)
        train_batches = 0
        for x in train_loader:
            x = x.to(device)
            out = model(x)
            x_hat = out["x_hat"]
            recon_mse = F.mse_loss(x_hat, x)
            recon_cos = (1.0 - F.cosine_similarity(x_hat, x, dim=-1)).mean()
            loss = recon_mse + args.cosine_weight * recon_cos + out["commit_loss"]
            opt.zero_grad(set_to_none=True)
            loss.backward()
            if args.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            opt.step()
            train_total["loss"] += float(loss.item())
            train_total["recon_mse"] += float(recon_mse.item())
            train_total["recon_cosloss"] += float(recon_cos.item())
            train_total["commit_loss"] += float(out["commit_loss"].item())
            train_batches += 1
        model.eval()
        val_total = defaultdict(float)
        val_batches = 0
        with torch.inference_mode():
            for x in val_loader:
                x = x.to(device)
                out = model(x)
                x_hat = out["x_hat"]
                recon_mse = F.mse_loss(x_hat, x)
                recon_cos = (1.0 - F.cosine_similarity(x_hat, x, dim=-1)).mean()
                loss = recon_mse + args.cosine_weight * recon_cos + out["commit_loss"]
                val_total["loss"] += float(loss.item())
                val_total["recon_mse"] += float(recon_mse.item())
                val_total["recon_cosloss"] += float(recon_cos.item())
                val_total["commit_loss"] += float(out["commit_loss"].item())
                val_batches += 1
                if args.max_val_batches and val_batches >= args.max_val_batches:
                    break
        rec = {
            "epoch": epoch,
            "train": {k: v / max(train_batches, 1) for k, v in train_total.items()},
            "val": {k: v / max(val_batches, 1) for k, v in val_total.items()},
        }
        history.append(rec)
        write_json(rqvae_dir / "train_history.json", history)
        print(json.dumps(rec, sort_keys=True), flush=True)
    torch.save({"model": model.state_dict(), "config": cfg}, rqvae_dir / "model.pt")
    write_json(rqvae_dir / "train_done.json", {"finished_at": now_utc(), "model": str(rqvae_dir / "model.pt")})
    append_progress(
        f"- Finished RQVAE training for `{args.lang}`.\n"
        f"- Model: `{rqvae_dir / 'model.pt'}`; history: `{rqvae_dir / 'train_history.json'}`."
    )


def cmd_encode_sids(args: argparse.Namespace) -> None:
    import torch
    import torch.nn.functional as F

    sys.path.insert(0, "/root")
    from rqvae_title_pipeline import RQVAE

    out_dir = Path(args.out_dir)
    variants_df = pd.read_parquet(out_dir / "variants" / "variants.parquet")
    hidden_meta = load_json(out_dir / "hidden" / "hidden_states_meta.json")
    hidden_path = Path(hidden_meta["memmap"])
    hidden_shape = tuple(hidden_meta["shape"])
    rqvae_dir = out_dir / "rqvae"
    ckpt = torch.load(rqvae_dir / "model.pt", map_location="cpu")
    cfg = ckpt["config"]
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    model = RQVAE(
        input_dim=int(hidden_shape[2]),
        latent_dim=int(cfg["latent_dim"]),
        num_codebooks=int(cfg["num_codebooks"]),
        codebook_size=int(cfg["codebook_size"]),
        beta_commit=float(cfg["beta_commit"]),
        ema_decay=float(cfg["ema_decay"]),
    ).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    hidden = np.memmap(hidden_path, dtype=np.float16, mode="r", shape=hidden_shape)
    sid_path = rqvae_dir / "sids.uint16.memmap"
    sids = np.memmap(
        sid_path,
        dtype=np.uint16,
        mode="w+",
        shape=(hidden_shape[0], hidden_shape[1], int(cfg["num_codebooks"])),
    )
    metrics: Dict[str, Any] = {
        "created_at": now_utc(),
        "sid_shape": [int(hidden_shape[0]), int(hidden_shape[1]), int(cfg["num_codebooks"])],
        "sid_memmap": str(sid_path),
        "codebook_size": int(cfg["codebook_size"]),
        "normalize": bool(cfg.get("normalize", True)),
        "by_layer": [],
    }
    append_progress(
        f"- Started SID encoding for `{args.lang}`.\n"
        f"- SID memmap target: `{sid_path}`."
    )
    with torch.inference_mode():
        for layer in range(hidden_shape[1]):
            counts = np.zeros((int(cfg["num_codebooks"]), int(cfg["codebook_size"])), dtype=np.int64)
            mse_sum = 0.0
            rel_sum = 0.0
            n_total = 0
            residual_sum = np.zeros(int(cfg["num_codebooks"]) + 1, dtype=np.float64)
            residual_batches = 0
            for start in range(0, hidden_shape[0], args.batch_size):
                end = min(start + args.batch_size, hidden_shape[0])
                x_np = np.asarray(hidden[start:end, layer], dtype=np.float32)
                if cfg.get("normalize", True):
                    norms = np.linalg.norm(x_np, axis=1, keepdims=True)
                    x_np = x_np / np.clip(norms, 1e-12, None)
                x = torch.from_numpy(x_np).to(device)
                out = model(x)
                x_hat = out["x_hat"]
                diff = x_hat - x
                mse = diff.pow(2).mean(dim=1)
                rel = diff.norm(dim=1) / torch.clamp(x.norm(dim=1), min=1e-12)
                mse_sum += float(mse.sum().item())
                rel_sum += float(rel.sum().item())
                n_total += int(end - start)
                for level, idx in enumerate(out["indices"]):
                    idx_np = idx.detach().cpu().numpy().astype(np.uint16)
                    sids[start:end, layer, level] = idx_np
                    counts[level] += np.bincount(idx_np, minlength=int(cfg["codebook_size"]))
                residual_sum += np.asarray([float(v.item()) for v in out["residual_norms"]])
                residual_batches += 1
            layer_metrics: Dict[str, Any] = {
                "layer": layer,
                "mse": mse_sum / max(n_total, 1),
                "relative_l2": rel_sum / max(n_total, 1),
                "residual_curve": (residual_sum / max(residual_batches, 1)).tolist(),
                "levels": [],
            }
            for level in range(int(cfg["num_codebooks"])):
                cnt = counts[level]
                p = cnt / max(cnt.sum(), 1)
                used = int((cnt > 0).sum())
                entropy = float(-(p[p > 0] * np.log(p[p > 0])).sum())
                layer_metrics["levels"].append(
                    {
                        "level": level,
                        "used_codes": used,
                        "usage_ratio": used / int(cfg["codebook_size"]),
                        "dead_codes": int((cnt == 0).sum()),
                        "dead_code_ratio": int((cnt == 0).sum()) / int(cfg["codebook_size"]),
                        "entropy": entropy,
                        "perplexity": float(np.exp(entropy)),
                    }
                )
            metrics["by_layer"].append(layer_metrics)
            sids.flush()
            print(f"encoded layer {layer}/{hidden_shape[1] - 1}", flush=True)
    write_json(rqvae_dir / "sid_metrics.json", metrics)
    write_json(
        rqvae_dir / "sids_meta.json",
        {
            "created_at": now_utc(),
            "shape": metrics["sid_shape"],
            "dtype": "uint16",
            "memmap": str(sid_path),
            "metrics": str(rqvae_dir / "sid_metrics.json"),
        },
    )
    append_progress(
        f"- Finished SID encoding for `{args.lang}`.\n"
        f"- SID shape: `{metrics['sid_shape']}`; metrics: `{rqvae_dir / 'sid_metrics.json'}`."
    )


GSM8K_FEWSHOT = [
    (
        "There are 15 trees in the grove. Grove workers will plant trees in the grove today. "
        "After they are done, there will be 21 trees. How many trees did the grove workers plant today?",
        "There are 15 trees originally. Then there were 21 trees after some more were planted. "
        "So there must have been 21 - 15 = 6.\n#### 6",
    ),
    (
        "If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?",
        "There are originally 3 cars. 2 more cars arrive. 3 + 2 = 5.\n#### 5",
    ),
    (
        "Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?",
        "Originally, Leah had 32 chocolates. Her sister had 42. So in total they had 32 + 42 = 74. "
        "After eating 35, they had 74 - 35 = 39.\n#### 39",
    ),
    (
        "Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. "
        "How many lollipops did Jason give to Denny?",
        "Jason started with 20 lollipops. Then he had 12 after giving some to Denny. "
        "So he gave Denny 20 - 12 = 8.\n#### 8",
    ),
    (
        "Shawn has five toys. For Christmas, he got two toys each from his mom and dad. "
        "How many toys does he have now?",
        "Shawn started with 5 toys. If he got 2 toys each from his mom and dad, "
        "then that is 4 more toys. 5 + 4 = 9.\n#### 9",
    ),
]


def make_eval_prompt(question: str, lang_name: str) -> str:
    parts = [f"Question: {q}\nAnswer: {a}" for q, a in GSM8K_FEWSHOT]
    parts.append(f"Question: {question}\nAnswer:")
    return "\n\n".join(parts)


def cmd_eval_generate(args: argparse.Namespace) -> None:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    rank, world, local_rank = get_rank_world(args)
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank % torch.cuda.device_count())
        device = torch.device("cuda", local_rank % torch.cuda.device_count())
    else:
        device = torch.device("cpu")
    out_dir = Path(args.out_dir)
    variants_df = pd.read_parquet(out_dir / "variants" / "variants.parquet")
    indices = np.arange(len(variants_df), dtype=np.int64)[rank::world]
    if args.limit:
        indices = indices[: args.limit]
    eval_dir = out_dir / "eval"
    ensure_dir(eval_dir)
    done_path = eval_dir / f"eval_rank{rank:02d}_of_{world:02d}.done.json"
    out_path = eval_dir / f"eval_rank{rank:02d}_of_{world:02d}.jsonl"
    if done_path.exists() and not args.overwrite:
        print(f"eval shard already done: {done_path}")
        return
    tokenizer = AutoTokenizer.from_pretrained(str(args.qwen_model), trust_remote_code=True)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model_kwargs = {"torch_dtype": torch.bfloat16, "trust_remote_code": True}
    if args.attn_implementation:
        model_kwargs["attn_implementation"] = args.attn_implementation
    model = AutoModelForCausalLM.from_pretrained(str(args.qwen_model), **model_kwargs)
    model.to(device)
    model.eval()
    model.config.use_cache = True
    write_json(
        eval_dir / f"eval_rank{rank:02d}_of_{world:02d}.started.json",
        {
            "started_at": now_utc(),
            "rank": rank,
            "world": world,
            "num_rows": int(len(indices)),
            "qwen_model": str(args.qwen_model),
            "batch_size": args.batch_size,
            "max_new_tokens": args.max_new_tokens,
        },
    )
    append_progress(
        f"- Started evaluation generation shard rank `{rank}`/`{world}` for `{args.lang}`.\n"
        f"- Rows in shard: `{len(indices)}`; output: `{out_path}`."
    )
    if out_path.exists() and args.overwrite:
        out_path.unlink()
    emitted = 0
    with torch.inference_mode():
        for start in range(0, len(indices), args.batch_size):
            rows = indices[start : start + args.batch_size]
            prompts = []
            for row_idx in rows:
                q = str(variants_df.iloc[int(row_idx)]["question"])
                content = make_eval_prompt(q, args.lang_name)
                if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
                    prompts.append(
                        tokenizer.apply_chat_template(
                            [{"role": "user", "content": content}],
                            tokenize=False,
                            add_generation_prompt=True,
                            enable_thinking=False,
                        )
                    )
                else:
                    prompts.append(content)
            enc = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=args.max_input_length,
                add_special_tokens=True,
            )
            input_len = int(enc["input_ids"].shape[1])
            enc = {k: v.to(device) for k, v in enc.items()}
            gen = model.generate(
                **enc,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            out_records = []
            for i, row_idx in enumerate(rows):
                new_tokens = gen[i, input_len:]
                text = tokenizer.decode(new_tokens, skip_special_tokens=True)
                target = variants_df.iloc[int(row_idx)].get("target")
                pred = extract_prediction(text)
                out_records.append(
                    {
                        "variant_row": int(row_idx),
                        "variant_id": str(variants_df.iloc[int(row_idx)]["variant_id"]),
                        "split": str(variants_df.iloc[int(row_idx)]["split"]),
                        "source_idx": int(variants_df.iloc[int(row_idx)]["source_idx"]),
                        "variant_idx": int(variants_df.iloc[int(row_idx)]["variant_idx"]),
                        "target": target,
                        "prediction": pred,
                        "correct": bool(numbers_equal(pred, target)),
                        "model_output": text,
                    }
                )
            append_jsonl(out_path, out_records)
            emitted += len(out_records)
            print(f"eval rank {rank}/{world} {emitted}/{len(indices)}", flush=True)
    write_json(done_path, {"finished_at": now_utc(), "rows": int(emitted), "jsonl": str(out_path)})
    append_progress(
        f"- Finished evaluation shard rank `{rank}`/`{world}` for `{args.lang}`.\n"
        f"- Rows: `{emitted}`; file: `{out_path}`."
    )


def cmd_merge_eval(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    variants_df = pd.read_parquet(out_dir / "variants" / "variants.parquet")
    eval_dir = out_dir / "eval"
    shard_files = sorted(eval_dir.glob("eval_rank*_of_*.jsonl"))
    if not shard_files:
        raise RuntimeError(f"no eval shard jsonl files in {eval_dir}")
    rows = []
    for path in shard_files:
        rows.extend(read_jsonl(path))
    eval_df = pd.DataFrame(rows).drop_duplicates("variant_row", keep="last")
    eval_df = eval_df.sort_values("variant_row").reset_index(drop=True)
    if len(eval_df):
        strict_predictions = []
        relaxed_predictions = []
        strict_else_relaxed_predictions = []
        strict_correct = []
        relaxed_correct = []
        strict_else_relaxed_correct = []
        for row in eval_df.itertuples(index=False):
            text = getattr(row, "model_output", "")
            target = getattr(row, "target", None)
            strict_pred = extract_prediction(text)
            relaxed_pred = extract_relaxed_prediction(text)
            strict_else_relaxed_pred = strict_pred if strict_pred is not None else relaxed_pred
            strict_predictions.append(strict_pred)
            relaxed_predictions.append(relaxed_pred)
            strict_else_relaxed_predictions.append(strict_else_relaxed_pred)
            strict_correct.append(bool(numbers_equal(strict_pred, target)))
            relaxed_correct.append(bool(numbers_equal(relaxed_pred, target)))
            strict_else_relaxed_correct.append(bool(numbers_equal(strict_else_relaxed_pred, target)))
        eval_df["strict_prediction"] = strict_predictions
        eval_df["relaxed_prediction"] = relaxed_predictions
        eval_df["strict_else_relaxed_prediction"] = strict_else_relaxed_predictions
        eval_df["strict_correct"] = strict_correct
        eval_df["relaxed_correct"] = relaxed_correct
        eval_df["strict_else_relaxed_correct"] = strict_else_relaxed_correct
        # Backward compatibility: existing analysis code reads prediction/correct.
        eval_df["prediction"] = eval_df["strict_prediction"]
        eval_df["correct"] = eval_df["strict_correct"]
    missing = sorted(set(range(len(variants_df))) - set(eval_df["variant_row"].astype(int).tolist()))
    eval_df.to_parquet(eval_dir / "eval_results.parquet", index=False)
    strict_parse_failures = int(eval_df["strict_prediction"].isna().sum()) if len(eval_df) else 0
    relaxed_parse_failures = int(eval_df["relaxed_prediction"].isna().sum()) if len(eval_df) else 0
    summary = {
        "created_at": now_utc(),
        "num_rows": int(len(eval_df)),
        "expected_rows": int(len(variants_df)),
        "missing_rows": len(missing),
        "missing_preview": missing[:20],
        "strict_format_accuracy": float(eval_df["strict_correct"].mean()) if len(eval_df) else None,
        "strict_accuracy_by_split": {
            str(k): float(v) for k, v in eval_df.groupby("split")["strict_correct"].mean().to_dict().items()
        },
        "strict_prediction_none": strict_parse_failures,
        "strict_prediction_none_rate": float(strict_parse_failures / len(eval_df)) if len(eval_df) else None,
        "relaxed_last_number_accuracy": float(eval_df["relaxed_correct"].mean()) if len(eval_df) else None,
        "relaxed_accuracy_by_split": {
            str(k): float(v) for k, v in eval_df.groupby("split")["relaxed_correct"].mean().to_dict().items()
        },
        "relaxed_prediction_none": relaxed_parse_failures,
        "relaxed_prediction_none_rate": float(relaxed_parse_failures / len(eval_df)) if len(eval_df) else None,
        "strict_else_relaxed_accuracy": float(eval_df["strict_else_relaxed_correct"].mean()) if len(eval_df) else None,
        "strict_else_relaxed_accuracy_by_split": {
            str(k): float(v)
            for k, v in eval_df.groupby("split")["strict_else_relaxed_correct"].mean().to_dict().items()
        },
        "format_failure_recovered_correct": int(
            ((eval_df["strict_prediction"].isna()) & (eval_df["relaxed_correct"])).sum()
        )
        if len(eval_df)
        else 0,
        "overall_accuracy": float(eval_df["strict_correct"].mean()) if len(eval_df) else None,
        "accuracy_by_split": {
            str(k): float(v) for k, v in eval_df.groupby("split")["strict_correct"].mean().to_dict().items()
        },
        "eval_results": str(eval_dir / "eval_results.parquet"),
    }
    write_json(eval_dir / "eval_summary.json", summary)
    append_progress(
        f"- Merged evaluation results for `{args.lang}`.\n"
        f"- Rows: `{len(eval_df)}` / expected `{len(variants_df)}`; missing `{len(missing)}`.\n"
        f"- Strict-format accuracy: `{summary['strict_format_accuracy']}`.\n"
        f"- Relaxed last-number accuracy: `{summary['relaxed_last_number_accuracy']}`.\n"
        f"- Strict-else-relaxed accuracy: `{summary['strict_else_relaxed_accuracy']}`."
    )
    if missing:
        raise RuntimeError(f"evaluation missing {len(missing)} rows")


def make_english_rewrite_messages(question: str) -> List[Dict[str, str]]:
    number_tokens = extract_number_tokens(question)
    number_line = ", ".join(number_tokens) if number_tokens else "(none)"
    system = (
        "Reasoning: low\n"
        "You rewrite grade-school math word problems. Preserve exact meaning, names, "
        "currency symbols, and all numbers exactly. Do not solve. Return only one strict JSON object."
    )
    user = (
        "Original question:\n"
        f"{question}\n\n"
        f"Exact numeric tokens that must appear in every rewrite, unchanged: {number_line}\n\n"
        "Write exactly 5 substantially different English rewrites. "
        "Change wording and sentence order as much as possible while preserving the exact meaning. "
        "Keep every number token exactly as written in the original question, including $, decimals, "
        "fractions, and commas. Do not convert digits to words, do not convert fractions to unicode "
        "symbols, and do not round or infer missing quantities. Keep all names unchanged. "
        "Do not add hints and do not solve.\n\n"
        "Return JSON with this shape only:\n"
        '{"rewrites":["rewrite one","rewrite two","rewrite three","rewrite four","rewrite five"]}'
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def cmd_rewrite_english(args: argparse.Namespace) -> None:
    rank, world, local_rank = get_rank_world(args)
    if world > 1 and args.tensor_parallel_size == 1 and "CUDA_VISIBLE_DEVICES" not in os.environ:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(local_rank)
    patch_vllm_tokenizer_cache_for_transformers5()
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import GuidedDecodingParams

    out_dir = Path(args.out_dir)
    ensure_dir(out_dir / "rewrites_en")
    if world > 1:
        records_path = out_dir / "rewrites_en" / f"english_rewrite_records_rank{rank:02d}_of_{world:02d}.jsonl"
    else:
        records_path = out_dir / "rewrites_en" / "english_rewrite_records.jsonl"
    existing = {} if args.force_rewrite else load_completed_english_rewrites(out_dir)
    only_keys = load_key_filter(args.only_missing_file)

    pending_rows: List[Dict[str, Any]] = []
    total_candidates = 0
    shard_candidates = 0
    skipped_existing_in_shard = 0
    english_root = Path(args.english_source_dir)
    target_source = pd.read_parquet(out_dir / "source.parquet")
    target_lookup = {
        (str(row["split"]), int(row["source_idx"])): row
        for row in target_source.to_dict("records")
    }
    for split in ["train", "test"]:
        if args.split and split not in set(args.split):
            continue
        df = pd.read_parquet(english_root / "main" / f"{split}-00000-of-00001.parquet")
        for i, row in df.reset_index(drop=True).iterrows():
            key_tuple = (split, int(i))
            if key_tuple not in target_lookup:
                continue
            if only_keys is not None and key_tuple not in only_keys:
                continue
            row_position = total_candidates
            total_candidates += 1
            if world > 1 and row_position % world != rank:
                continue
            shard_candidates += 1
            if key_tuple in existing:
                skipped_existing_in_shard += 1
                continue
            pending_rows.append(
                {
                    "split": split,
                    "source_idx": int(i),
                    "english_question": str(row["question"]),
                    "target_question": str(target_lookup[key_tuple]["question"]),
                    "answer": str(target_lookup[key_tuple]["answer"]),
                    "target": target_lookup[key_tuple].get("target"),
                }
            )
    if args.limit:
        pending_rows = pending_rows[: args.limit]

    write_json(
        out_dir / "rewrites_en" / "english_rewrite_run_meta.json",
        {
            "started_at": now_utc(),
            "model": str(args.rewrite_model),
            "lang": args.lang,
            "english_source_dir": str(english_root),
            "rank": rank,
            "world": world,
            "only_missing_file": str(args.only_missing_file) if args.only_missing_file else None,
            "force_rewrite": bool(args.force_rewrite),
            "already_completed": len(existing),
            "total_candidates": total_candidates,
            "shard_candidates": shard_candidates,
            "skipped_existing_in_shard": skipped_existing_in_shard,
            "pending_this_run": len(pending_rows),
            "batch_size": args.batch_size,
            "num_candidates": args.num_candidates,
        },
    )
    append_progress(
        f"- Started English rewrite stage for target `{args.lang}`.\n"
        f"- Shard rank/world: `{rank}/{world}`; existing complete English rewrite records: `{len(existing)}`; "
        f"total candidates: `{total_candidates}`; shard candidates: `{shard_candidates}`; "
        f"skipped existing in shard: `{skipped_existing_in_shard}`; pending in this run: `{len(pending_rows)}`.\n"
        f"- Output file: `{records_path}`."
    )
    if not pending_rows:
        return

    llm_kwargs: Dict[str, Any] = {
        "model": str(args.rewrite_model),
        "trust_remote_code": True,
        "tensor_parallel_size": args.tensor_parallel_size,
        "gpu_memory_utilization": args.gpu_memory_utilization,
        "max_model_len": args.max_model_len,
        "enable_prefix_caching": True,
        "hf_overrides": {"rope_theta": args.rope_theta},
        "disable_custom_all_reduce": args.disable_custom_all_reduce,
        "enforce_eager": args.enforce_eager,
    }
    if args.max_num_seqs:
        llm_kwargs["max_num_seqs"] = args.max_num_seqs
    llm = LLM(**llm_kwargs)

    guided_decoding = None
    if args.guided_json:
        guided_decoding = GuidedDecodingParams.from_optional(
            json={
                "type": "object",
                "additionalProperties": False,
                "required": ["rewrites"],
                "properties": {
                    "rewrites": {
                        "type": "array",
                        "minItems": 5,
                        "maxItems": 5,
                        "items": {"type": "string"},
                    }
                },
            }
        )
    sampling = SamplingParams(
        n=args.num_candidates,
        temperature=args.temperature,
        top_p=args.top_p,
        presence_penalty=args.presence_penalty,
        frequency_penalty=args.frequency_penalty,
        repetition_penalty=args.repetition_penalty,
        max_tokens=args.max_tokens,
        guided_decoding=guided_decoding,
    )

    total_ok = 0
    total_bad = 0
    for start in range(0, len(pending_rows), args.batch_size):
        batch = pending_rows[start : start + args.batch_size]
        messages = [make_english_rewrite_messages(row["english_question"]) for row in batch]
        outputs = llm.chat(
            messages,
            sampling_params=sampling,
            use_tqdm=False,
            chat_template_kwargs={"reasoning_effort": args.reasoning_effort},
        )
        out_records = []
        for row, out in zip(batch, outputs):
            candidate_results = []
            best_rewrites: List[str] = []
            best_raw = ""
            best_err: Optional[str] = "no outputs"
            best_candidate_idx = -1
            for candidate_idx, candidate in enumerate(out.outputs or []):
                raw = candidate.text
                rewrites, err = parse_rewrites(raw, row["english_question"], expected=5)
                candidate_results.append(
                    {
                        "candidate_idx": candidate_idx,
                        "error": err,
                        "rewrites": rewrites,
                        "raw_output": raw,
                    }
                )
                if err is None:
                    best_rewrites = rewrites
                    best_raw = raw
                    best_err = None
                    best_candidate_idx = candidate_idx
                    break
                if best_candidate_idx < 0:
                    best_rewrites = rewrites
                    best_raw = raw
                    best_err = err
                    best_candidate_idx = candidate_idx
            status = "ok" if best_err is None else "bad"
            total_ok += int(status == "ok")
            total_bad += int(status != "ok")
            out_records.append(
                {
                    "status": status,
                    "error": best_err,
                    "split": row["split"],
                    "source_idx": int(row["source_idx"]),
                    "english_question": row["english_question"],
                    "target_question": row["target_question"],
                    "answer": row["answer"],
                    "target": row.get("target"),
                    "rewrites": best_rewrites,
                    "raw_output": best_raw,
                    "candidate_idx": best_candidate_idx,
                    "candidate_results": candidate_results,
                    "model": str(args.rewrite_model),
                    "lang": args.lang,
                    "created_at": now_utc(),
                }
            )
        append_jsonl(records_path, out_records)
        print(
            f"english rewrite progress {min(start + len(batch), len(pending_rows))}/{len(pending_rows)} "
            f"ok={total_ok} bad={total_bad}",
            flush=True,
        )
    append_progress(
        f"- Finished English rewrite run for target `{args.lang}`.\n"
        f"- This run parsed ok records: `{total_ok}`; bad records: `{total_bad}`.\n"
        f"- English rewrite records are in `{records_path}`."
    )


def cmd_translate_rewrites(args: argparse.Namespace) -> None:
    import importlib
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    nllb = importlib.import_module("translate_gsm8k_nllb_direct")
    out_dir = Path(args.out_dir)
    english_paths = english_rewrite_record_paths(out_dir)
    if not english_paths:
        raise FileNotFoundError(f"missing English rewrite records under: {out_dir / 'rewrites_en'}")
    final_path = out_dir / "rewrites" / "rewrite_records.jsonl"
    existing = load_completed_rewrites(final_path)
    force_keys = load_key_filter(args.force_keys_file)

    english_record_map: Dict[Tuple[str, int], Dict[str, Any]] = {}
    for english_path in english_paths:
        for rec in read_jsonl(english_path):
            key_tuple = (str(rec.get("split")), int(rec.get("source_idx")))
            if force_keys is not None and key_tuple not in force_keys:
                continue
            if key_tuple in existing and (force_keys is None or key_tuple not in force_keys):
                continue
            if rec.get("status") == "ok" and len(rec.get("rewrites") or []) == 5:
                english_record_map[key_tuple] = rec
    english_records = []
    for key_tuple in sorted(english_record_map):
        rec = english_record_map[key_tuple]
        key_tuple = (str(rec.get("split")), int(rec.get("source_idx")))
        english_records.append(rec)
    if args.limit:
        english_records = english_records[: args.limit]

    append_progress(
        f"- Started translating English rewrites to `{args.lang}`.\n"
        f"- Existing final rewrite records: `{len(existing)}`; pending in this run: `{len(english_records)}`.\n"
        f"- Force keys file: `{args.force_keys_file}`; English input files: `{len(english_paths)}`; output file: `{final_path}`."
    )
    if not english_records:
        return

    device = args.device
    if device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
    tokenizer = AutoTokenizer.from_pretrained(args.nllb_model, src_lang="eng_Latn")
    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.nllb_model,
        dtype=torch.float16 if device == "cuda" else torch.float32,
        attn_implementation="eager",
    ).to(device)
    model.eval()

    units: Dict[str, str] = {}
    for rec in english_records:
        for text in rec.get("rewrites") or []:
            for unit in nllb.translatable_units(text):
                units.setdefault(nllb.key(unit), unit)

    cache_path = out_dir / ".cache" / f"english_rewrites__{args.lang}.jsonl"
    cache = nllb.load_cache(cache_path)
    missing = [(text_key, text) for text_key, text in units.items() if text_key not in cache]
    nllb.translate_missing(
        model=model,
        tokenizer=tokenizer,
        missing=missing,
        target_lang=args.lang,
        cache_path=cache_path,
        cache=cache,
        batch_size=args.batch_size,
        source_max_length=args.source_max_length,
        target_max_length=args.target_max_length,
        device=device,
    )

    out_records = []
    total_ok = 0
    total_bad = 0
    for rec in english_records:
        translated = [nllb.reconstruct_text(text, cache) for text in rec.get("rewrites") or []]
        err = None
        if len(translated) != 5:
            err = f"expected 5 translated rewrites, got {len(translated)}"
        if err is None:
            err = validate_rewrite_numbers(translated, rec.get("target_question") or "")
        if err is None:
            err = validate_rewrite_language(translated, args.lang)
        status = "ok" if err is None else "bad"
        total_ok += int(status == "ok")
        total_bad += int(status != "ok")
        out_records.append(
            {
                "status": status,
                "error": err,
                "split": rec["split"],
                "source_idx": int(rec["source_idx"]),
                "question": rec["target_question"],
                "answer": rec["answer"],
                "target": rec.get("target"),
                "rewrites": translated,
                "english_rewrites": rec.get("rewrites"),
                "raw_output": rec.get("raw_output"),
                "model": f"{rec.get('model')} + {args.nllb_model}",
                "lang": args.lang,
                "created_at": now_utc(),
            }
        )
    append_jsonl(final_path, out_records)
    append_progress(
        f"- Finished translating English rewrites to `{args.lang}`.\n"
        f"- This run final ok records: `{total_ok}`; bad records: `{total_bad}`.\n"
        f"- Final rewrite records are in `{final_path}`."
    )


def wilson_lower(c: np.ndarray, n: np.ndarray, z: float = 1.96) -> np.ndarray:
    n_safe = np.maximum(n, 1)
    phat = c / n_safe
    denom = 1.0 + z * z / n_safe
    center = phat + z * z / (2 * n_safe)
    margin = z * np.sqrt((phat * (1 - phat) + z * z / (4 * n_safe)) / n_safe)
    return (center - margin) / denom


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    p = np.asarray(pvals, dtype=np.float64)
    order = np.argsort(p)
    q = np.empty_like(p)
    prev = 1.0
    m = len(p)
    for rank in range(m, 0, -1):
        idx = order[rank - 1]
        val = p[idx] * m / rank
        prev = min(prev, val)
        q[idx] = min(prev, 1.0)
    return q


def cmd_analyze(args: argparse.Namespace) -> None:
    from scipy.stats import fisher_exact

    out_dir = Path(args.out_dir)
    variants_df = pd.read_parquet(out_dir / "variants" / "variants.parquet")
    eval_df = pd.read_parquet(out_dir / "eval" / "eval_results.parquet")
    merged = variants_df.merge(eval_df[["variant_row", "correct"]], on="variant_row", how="left")
    if merged["correct"].isna().any():
        raise RuntimeError("missing correctness values; run merge-eval first")
    sids_meta = load_json(out_dir / "rqvae" / "sids_meta.json")
    sid_shape = tuple(sids_meta["shape"])
    sids = np.memmap(sids_meta["memmap"], dtype=np.uint16, mode="r", shape=sid_shape)
    codebook_size = int(load_json(out_dir / "rqvae" / "train_config.json")["codebook_size"])
    train_rows = merged.index[merged["split"] == "train"].to_numpy(dtype=np.int64)
    test_rows = merged.index[merged["split"] == "test"].to_numpy(dtype=np.int64)
    correct = merged["correct"].astype(bool).to_numpy()
    baseline_train = float(correct[train_rows].mean())
    baseline_all = float(correct.mean())
    total_correct = int(correct[train_rows].sum())
    total_n = int(len(train_rows))
    bucket_records: List[Dict[str, Any]] = []
    pvals: List[float] = []
    for layer in range(sid_shape[1]):
        for level in range(sid_shape[2]):
            vals = np.asarray(sids[train_rows, layer, level], dtype=np.int32)
            n = np.bincount(vals, minlength=codebook_size)
            c = np.bincount(vals, weights=correct[train_rows].astype(np.int32), minlength=codebook_size)
            lower = wilson_lower(c, n)
            for sid in range(codebook_size):
                if n[sid] < args.min_bucket_n:
                    continue
                hit_correct = int(c[sid])
                hit_wrong = int(n[sid] - c[sid])
                other_correct = int(total_correct - hit_correct)
                other_wrong = int((total_n - n[sid]) - other_correct)
                _, p = fisher_exact(
                    [[hit_correct, hit_wrong], [other_correct, other_wrong]],
                    alternative="greater",
                )
                pvals.append(float(p))
                rate = hit_correct / max(int(n[sid]), 1)
                bucket_records.append(
                    {
                        "layer": layer,
                        "level": level,
                        "sid": sid,
                        "n": int(n[sid]),
                        "correct": hit_correct,
                        "accuracy": rate,
                        "uplift": rate - baseline_train,
                        "wilson_lower": float(lower[sid]),
                        "p_value": float(p),
                    }
                )
    if bucket_records:
        qvals = bh_fdr(np.asarray(pvals, dtype=np.float64))
        for rec, q in zip(bucket_records, qvals):
            rec["q_value"] = float(q)
            rec["selected"] = bool(
                rec["q_value"] <= args.fdr
                and rec["wilson_lower"] > baseline_train
                and rec["uplift"] > 0
            )
    buckets_df = pd.DataFrame(bucket_records)
    analysis_dir = out_dir / "analysis"
    ensure_dir(analysis_dir)
    buckets_df.to_parquet(analysis_dir / "sid_buckets.parquet", index=False)
    selected_rules = buckets_df[buckets_df["selected"]].copy() if len(buckets_df) else buckets_df
    selected_rules.to_parquet(analysis_dir / "significant_sid_rules.parquet", index=False)
    score_map: Dict[Tuple[int, int, int], float] = {}
    for rec in selected_rules.to_dict("records"):
        weight = float(rec["uplift"]) * max(1.0, -math.log10(max(float(rec["q_value"]), 1e-300)))
        score_map[(int(rec["layer"]), int(rec["level"]), int(rec["sid"]))] = weight

    selection_rows: List[Dict[str, Any]] = []
    test_df = merged.loc[test_rows].copy()
    for source_idx, group in test_df.groupby("source_idx", sort=True):
        best_row = None
        best_score = None
        for row in group.to_dict("records"):
            ridx = int(row["variant_row"])
            score = 0.0
            for layer in range(sid_shape[1]):
                for level in range(sid_shape[2]):
                    score += score_map.get((layer, level, int(sids[ridx, layer, level])), 0.0)
            if best_score is None or score > best_score or (
                score == best_score and int(row["variant_idx"]) == 0
            ):
                best_score = score
                best_row = row
        assert best_row is not None
        selection_rows.append(
            {
                "source_idx": int(source_idx),
                "selected_variant_row": int(best_row["variant_row"]),
                "selected_variant_idx": int(best_row["variant_idx"]),
                "score": float(best_score or 0.0),
                "correct": bool(best_row["correct"]),
            }
        )
    selection_df = pd.DataFrame(selection_rows)
    selection_df.to_parquet(analysis_dir / "test_selection.parquet", index=False)
    original_test = test_df[test_df["variant_idx"] == 0]
    summary = {
        "created_at": now_utc(),
        "baseline_all_accuracy": baseline_all,
        "baseline_train_accuracy": baseline_train,
        "test_all_variant_accuracy": float(test_df["correct"].mean()) if len(test_df) else None,
        "test_original_accuracy": float(original_test["correct"].mean()) if len(original_test) else None,
        "test_selected_accuracy": float(selection_df["correct"].mean()) if len(selection_df) else None,
        "num_bucket_tests": int(len(buckets_df)),
        "num_significant_rules": int(len(selected_rules)),
        "min_bucket_n": args.min_bucket_n,
        "fdr": args.fdr,
        "sid_buckets": str(analysis_dir / "sid_buckets.parquet"),
        "significant_sid_rules": str(analysis_dir / "significant_sid_rules.parquet"),
        "test_selection": str(analysis_dir / "test_selection.parquet"),
    }
    write_json(analysis_dir / "analysis_summary.json", summary)
    append_progress(
        f"- Finished SID correctness analysis for `{args.lang}`.\n"
        f"- Baseline train accuracy: `{baseline_train}`; test original: `{summary['test_original_accuracy']}`; "
        f"test selected: `{summary['test_selected_accuracy']}`.\n"
        f"- Significant SID rules: `{len(selected_rules)}`; summary: `{analysis_dir / 'analysis_summary.json'}`."
    )


def cmd_audit(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, evidence: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "evidence": evidence})

    add("prepare_meta", (out_dir / "prepare_meta.json").exists(), str(out_dir / "prepare_meta.json"))
    if (out_dir / "source.parquet").exists():
        source_df = pd.read_parquet(out_dir / "source.parquet")
        add("source_counts", len(source_df) == 7473 + 1319, f"rows={len(source_df)}")
    else:
        add("source_counts", False, "source.parquet missing")
    rewrite_path = out_dir / "rewrites" / "rewrite_records.jsonl"
    if rewrite_path.exists():
        complete = load_completed_rewrites(rewrite_path)
        add("rewrite_complete_records", len(complete) == 7473 + 1319, f"complete={len(complete)}")
    else:
        add("rewrite_complete_records", False, "rewrite_records.jsonl missing")
    variants_path = out_dir / "variants" / "variants.parquet"
    if variants_path.exists():
        variants_df = pd.read_parquet(variants_path)
        train_n = int((variants_df["split"] == "train").sum())
        test_n = int((variants_df["split"] == "test").sum())
        add("variant_counts", train_n == 7473 * 6 and test_n == 1319 * 6, f"train={train_n}, test={test_n}")
    else:
        variants_df = None
        add("variant_counts", False, "variants.parquet missing")
    hidden_meta_path = out_dir / "hidden" / "hidden_states_meta.json"
    if hidden_meta_path.exists():
        meta = load_json(hidden_meta_path)
        ok = meta.get("shape", [None, None, None])[1:] == [33, 4096] and meta.get("missing_rows") == 0
        add("hidden_states", ok, json.dumps(meta, ensure_ascii=False))
    else:
        add("hidden_states", False, "hidden_states_meta.json missing")
    sid_meta_path = out_dir / "rqvae" / "sids_meta.json"
    add("sids", sid_meta_path.exists(), str(sid_meta_path))
    eval_summary_path = out_dir / "eval" / "eval_summary.json"
    if eval_summary_path.exists():
        meta = load_json(eval_summary_path)
        add("eval_results", meta.get("missing_rows") == 0, json.dumps(meta, ensure_ascii=False))
    else:
        add("eval_results", False, "eval_summary.json missing")
    analysis_summary_path = out_dir / "analysis" / "analysis_summary.json"
    add("analysis", analysis_summary_path.exists(), str(analysis_summary_path))
    ok_all = all(c["ok"] for c in checks)
    report = {"created_at": now_utc(), "ok": ok_all, "checks": checks}
    write_json(out_dir / "audit_report.json", report)
    append_progress(
        f"- Ran completion audit for `{args.lang}`.\n"
        f"- Overall complete: `{ok_all}`; report: `{out_dir / 'audit_report.json'}`."
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not ok_all:
        raise SystemExit(1)


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--lang", default=DEFAULT_LANG)
    parser.add_argument("--lang-name", default=DEFAULT_LANG_NAME)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)


def add_rewrite_runtime_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--rewrite-model", type=Path, default=DEFAULT_REWRITE_MODEL)
    parser.add_argument("--split", nargs="*", choices=["train", "test"])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--tensor-parallel-size", type=int, default=1)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--max-num-seqs", type=int, default=0)
    parser.add_argument("--rope-theta", type=float, default=150000.0)
    parser.add_argument("--disable-custom-all-reduce", action="store_true")
    parser.add_argument("--enforce-eager", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.75)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--presence-penalty", type=float, default=0.0)
    parser.add_argument("--frequency-penalty", type=float, default=0.0)
    parser.add_argument("--repetition-penalty", type=float, default=1.0)
    parser.add_argument("--num-candidates", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default="low")
    parser.add_argument("--guided-json", action="store_true")
    parser.add_argument("--guided-backend", default="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Single-language GSM8K rewrite/SID experiment")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare")
    add_common(p)
    p.set_defaults(func=cmd_prepare)

    p = sub.add_parser("rewrite")
    add_common(p)
    add_rewrite_runtime_args(p)
    p.set_defaults(func=cmd_rewrite)

    p = sub.add_parser("rewrite-english")
    add_common(p)
    add_rewrite_runtime_args(p)
    p.add_argument("--english-source-dir", type=Path, default=Path("/root/gsm8k"))
    p.add_argument("--only-missing-file", type=Path)
    p.add_argument("--force-rewrite", action="store_true")
    p.add_argument("--rank", type=int, default=0)
    p.add_argument("--world-size", type=int, default=1)
    p.set_defaults(func=cmd_rewrite_english)

    p = sub.add_parser("translate-rewrites")
    add_common(p)
    p.add_argument("--nllb-model", type=Path, default=Path("/root/nllb-200-1.3B"))
    p.add_argument("--device", default="cuda")
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--source-max-length", type=int, default=512)
    p.add_argument("--target-max-length", type=int, default=512)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--force-keys-file", type=Path)
    p.set_defaults(func=cmd_translate_rewrites)

    p = sub.add_parser("build-variants")
    add_common(p)
    p.add_argument("--allow-incomplete", action="store_true")
    p.set_defaults(func=cmd_build_variants)

    p = sub.add_parser("extract-hidden")
    add_common(p)
    p.add_argument("--qwen-model", type=Path, default=DEFAULT_QWEN_MODEL)
    p.add_argument("--rank", type=int, default=0)
    p.add_argument("--world-size", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--length-batch-size", type=int, default=1024)
    p.add_argument("--max-length", type=int, default=1024)
    p.add_argument("--attn-implementation", default="flash_attention_2")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_extract_hidden)

    p = sub.add_parser("merge-hidden")
    add_common(p)
    p.add_argument("--chunk-size", type=int, default=256)
    p.set_defaults(func=cmd_merge_hidden)

    p = sub.add_parser("train-rqvae")
    add_common(p)
    p.add_argument("--device", default="cuda")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--latent-dim", type=int, default=256)
    p.add_argument("--num-codebooks", type=int, default=3)
    p.add_argument("--codebook-size", type=int, default=256)
    p.add_argument("--beta-commit", type=float, default=0.25)
    p.add_argument("--ema-decay", type=float, default=0.99)
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--batch-size", type=int, default=2048)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--cosine-weight", type=float, default=0.1)
    p.add_argument("--grad-clip", type=float, default=1.0)
    p.add_argument("--val-ratio", type=float, default=0.02)
    p.add_argument("--max-val-batches", type=int, default=200)
    p.add_argument("--num-workers", type=int, default=0)
    p.add_argument("--no-normalize", action="store_true")
    p.add_argument("--limit-variants", type=int, default=0)
    p.set_defaults(func=cmd_train_rqvae)

    p = sub.add_parser("encode-sids")
    add_common(p)
    p.add_argument("--device", default="cuda")
    p.add_argument("--batch-size", type=int, default=4096)
    p.set_defaults(func=cmd_encode_sids)

    p = sub.add_parser("eval-generate")
    add_common(p)
    p.add_argument("--qwen-model", type=Path, default=DEFAULT_QWEN_MODEL)
    p.add_argument("--rank", type=int, default=0)
    p.add_argument("--world-size", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--max-input-length", type=int, default=1024)
    p.add_argument("--max-new-tokens", type=int, default=256)
    p.add_argument("--attn-implementation", default="flash_attention_2")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_eval_generate)

    p = sub.add_parser("merge-eval")
    add_common(p)
    p.set_defaults(func=cmd_merge_eval)

    p = sub.add_parser("analyze")
    add_common(p)
    p.add_argument("--min-bucket-n", type=int, default=100)
    p.add_argument("--fdr", type=float, default=0.05)
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("audit")
    add_common(p)
    p.set_defaults(func=cmd_audit)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
