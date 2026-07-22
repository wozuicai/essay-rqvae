#!/usr/bin/env python3
import json
import re
from pathlib import Path

import pandas as pd


REPORT = Path("/root/gsm8k_sid_score_collection_linguistic_analysis.md")
BASE = Path("/root/gsm8k_single_language_experiment")
EN_TEST = Path("/root/gsm8k/main/test-00000-of-00001.parquet")
OUT_JSON = Path("/root/gsm8k_sid_case_semantic_check.json")
OUT_MD = Path("/root/gsm8k_sid_case_semantic_check.md")


def extract_cases() -> list[tuple[str, int, int]]:
    md = REPORT.read_text(encoding="utf-8")
    cases = []
    lang = None
    for line in md.splitlines():
        m = re.match(r"## ([a-z]{3}_[A-Za-z]+)$", line.strip())
        if m:
            lang = m.group(1)
        m = re.search(r"source_idx `([0-9]+)`, selected variant `([0-9]+)`", line)
        if m and lang:
            cases.append((lang, int(m.group(1)), int(m.group(2))))
    return cases


def nums(text: str) -> list[str]:
    return re.findall(r"\$?\d+(?:,\d{3})*(?:\.\d+)?(?:/\d+)?%?", str(text))


def short(text: str, n: int = 320) -> str:
    s = " ".join(str(text).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def heuristic_status(en_q: str, sel_q: str) -> tuple[str, list[str]]:
    en_nums = set(nums(en_q))
    sel_nums = set(nums(sel_q))
    reasons = []
    # Do not require exact equality because translations can preserve percentages
    # as decimals or omit implicit numbers, but large missing sets are suspicious.
    missing = sorted(en_nums - sel_nums)
    extra = sorted(sel_nums - en_nums)
    if len(missing) >= 3:
        reasons.append(f"many_missing_numbers={missing[:6]}")
    if len(extra) >= 4:
        reasons.append(f"many_extra_numbers={extra[:6]}")
    if re.search(r"\[P\]|\[P\d+\]|\[\d+\]", sel_q):
        reasons.append("placeholder_residue")
    if max_run(sel_q) >= 5:
        reasons.append("repetition_run")
    if len(sel_q.split()) <= 6:
        reasons.append("too_short")
    status = "likely_ok" if not reasons else "needs_manual_review"
    return status, reasons


def max_run(text: str) -> int:
    toks = re.findall(r"[\w\u0080-\uffff'-]+", str(text).casefold())
    best = cur = 0
    prev = None
    for tok in toks:
        if tok == prev:
            cur += 1
        else:
            cur = 1
            prev = tok
        best = max(best, cur)
    return best


def main() -> None:
    en = pd.read_parquet(EN_TEST)
    rows = []
    for lang, source_idx, variant_idx in extract_cases():
        out = BASE / lang
        variants = pd.read_parquet(out / "variants/variants.parquet")
        eval_df = pd.read_parquet(out / "eval/eval_results.parquet")
        selected = variants[
            (variants["split"] == "test")
            & (variants["source_idx"].astype(int) == source_idx)
            & (variants["variant_idx"].astype(int) == variant_idx)
        ].iloc[0]
        original = variants[
            (variants["split"] == "test")
            & (variants["source_idx"].astype(int) == source_idx)
            & (variants["variant_idx"].astype(int) == 0)
        ].iloc[0]
        eval_row = eval_df[eval_df["variant_row"].astype(int) == int(selected["variant_row"])].iloc[0]
        en_q = str(en.iloc[source_idx]["question"])
        sel_q = str(selected["question"])
        status, reasons = heuristic_status(en_q, sel_q)
        rows.append(
            {
                "lang": lang,
                "source_idx": source_idx,
                "selected_variant_idx": variant_idx,
                "target": selected.get("target"),
                "prediction": eval_row.get("strict_else_relaxed_prediction"),
                "correct": bool(eval_row.get("strict_else_relaxed_correct")),
                "heuristic_status": status,
                "heuristic_reasons": reasons,
                "english_numbers": nums(en_q),
                "selected_numbers": nums(sel_q),
                "english_question": en_q,
                "original_v0": str(original["question"]),
                "selected_question": sel_q,
            }
        )
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# SID Case Semantic Check",
        "",
        "This file checks whether examples used in the SID linguistic report appear semantically aligned with the original English GSM8K question. The status is heuristic; use it to decide which examples need manual review before paper use.",
        "",
        "| lang | source_idx | selected v | status | reasons | correct |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        md.append(
            f"| {row['lang']} | {row['source_idx']} | {row['selected_variant_idx']} | "
            f"{row['heuristic_status']} | {'; '.join(row['heuristic_reasons'])} | {row['correct']} |"
        )
    for row in rows:
        md += [
            "",
            f"## {row['lang']} source_idx={row['source_idx']} selected_v={row['selected_variant_idx']}",
            "",
            f"- Status: `{row['heuristic_status']}`; reasons: `{'; '.join(row['heuristic_reasons'])}`",
            f"- Target/prediction: `{row['target']}` / `{row['prediction']}`",
            f"- English: {short(row['english_question'])}",
            f"- Original v0: {short(row['original_v0'])}",
            f"- Selected: {short(row['selected_question'])}",
        ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == "__main__":
    main()
