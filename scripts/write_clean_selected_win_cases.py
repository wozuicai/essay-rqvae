#!/usr/bin/env python3
import json
import re
from pathlib import Path

import pandas as pd


BASE = Path("/root/gsm8k_single_language_experiment")
EN_TEST = Path("/root/gsm8k/main/test-00000-of-00001.parquet")
LANGS = ["npi_Deva", "sin_Sinh", "som_Latn", "swh_Latn", "yor_Latn", "zul_Latn"]

PLACEHOLDER_RE = re.compile(
    r"\[\s*P\s*\]|\[\s*P\s*\d+\s*\]|\[\s*\d+\s*\]|\bP\d+\b|(?<=-)P\d+\b|(?<=\s)P\d+\b",
    re.IGNORECASE,
)
PAGE_RE = re.compile(
    r"\[[^\]]*(?:page|página|පිටුව|पृष्ठ|ገጽ|စာမျက်နှာ|ទំព័រ|ຫນ້າ|"
    r"صفحة|shafi|ukurasa|iwe|oju|ikhasi)[^\]]*\]",
    re.IGNORECASE,
)
NUM_RE = re.compile(r"\$?\d+(?:,\d{3})*(?:\.\d+)?(?:/\d+)?%?")


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


def quality_ok(text: str) -> tuple[bool, list[str]]:
    text = str(text or "").strip()
    reasons = []
    if len(text.split()) <= 6:
        reasons.append("too_short")
    if PLACEHOLDER_RE.search(text):
        reasons.append("placeholder_residue")
    if PAGE_RE.search(text):
        reasons.append("page_marker")
    if max_run(text) >= 5:
        reasons.append("repeated_token_run")
    if text and not re.search(r"[A-Za-z\u0080-\uffff]", text):
        reasons.append("no_words")
    return (not reasons), reasons


def nums(text: str) -> list[str]:
    return NUM_RE.findall(str(text))


def short(text: str, n: int = 300) -> str:
    s = " ".join(str(text).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def main() -> None:
    en = pd.read_parquet(EN_TEST)
    all_results = []
    lines = [
        "# Clean Selected-Win Cases",
        "",
        "These cases satisfy all of the following:",
        "",
        "- original `variant_idx=0` is wrong under `strict_else_relaxed_correct`",
        "- SID-selected variant is correct under `strict_else_relaxed_correct`",
        "- both original v0 and selected question pass a conservative surface-quality filter",
        "- selected question has no obvious number loss compared with the English source under a simple heuristic",
        "",
        "These are the safer examples for arguing that SID selection changes the model outcome. Cases where both original and selected are correct are intentionally excluded.",
        "",
    ]
    for lang in LANGS:
        out = BASE / lang
        variants = pd.read_parquet(out / "variants/variants.parquet")
        eval_df = pd.read_parquet(out / "eval/eval_results.parquet")
        merged = variants.merge(
            eval_df[
                [
                    "variant_row",
                    "strict_prediction",
                    "relaxed_prediction",
                    "strict_else_relaxed_prediction",
                    "strict_correct",
                    "relaxed_correct",
                    "strict_else_relaxed_correct",
                ]
            ],
            on="variant_row",
            how="left",
            validate="one_to_one",
        )
        test = merged[merged["split"] == "test"].copy()
        original = test[test["variant_idx"] == 0][
            [
                "source_idx",
                "variant_row",
                "question",
                "target",
                "strict_else_relaxed_prediction",
                "strict_else_relaxed_correct",
            ]
        ].rename(
            columns={
                "variant_row": "original_variant_row",
                "question": "original_question",
                "strict_else_relaxed_prediction": "original_prediction",
                "strict_else_relaxed_correct": "original_correct",
            }
        )
        selection = pd.read_parquet(out / "analysis/test_selection_with_eval_metrics.parquet")
        if "source_idx" not in selection.columns and "source_idx_x" in selection.columns:
            selection = selection.rename(columns={"source_idx_x": "source_idx"})
        selected = selection.merge(
            test[["variant_row", "question"]],
            left_on="selected_variant_row",
            right_on="variant_row",
            how="left",
            validate="one_to_one",
        ).merge(original, on="source_idx", how="left", suffixes=("", "_orig"))

        rows = []
        for _, row in selected.iterrows():
            if bool(row["original_correct"]) or not bool(row["strict_else_relaxed_correct"]):
                continue
            if int(row["selected_variant_idx"]) == 0:
                continue
            original_ok, original_reasons = quality_ok(row["original_question"])
            selected_ok, selected_reasons = quality_ok(row["question"])
            if not (original_ok and selected_ok):
                continue
            en_q = str(en.iloc[int(row["source_idx"])]["question"])
            en_nums = set(nums(en_q))
            sel_nums = set(nums(row["question"]))
            missing = sorted(en_nums - sel_nums)
            # Keep only examples with no large number-loss signal. Allow small
            # differences because percentages/fractions can be expressed
            # differently across translations.
            if len(missing) >= 3:
                continue
            rows.append(
                {
                    "source_idx": int(row["source_idx"]),
                    "selected_variant_idx": int(row["selected_variant_idx"]),
                    "score": float(row["score"]),
                    "target": row.get("target"),
                    "original_prediction": row.get("original_prediction"),
                    "selected_prediction": row.get("strict_else_relaxed_prediction"),
                    "english_question": en_q,
                    "original_question": str(row["original_question"]),
                    "selected_question": str(row["question"]),
                    "missing_numbers_from_selected": missing,
                }
            )
        rows = sorted(rows, key=lambda r: r["score"], reverse=True)
        all_results.append({"lang": lang, "num_clean_selected_wins": len(rows), "cases": rows[:20]})

        lines += [
            f"## {lang}",
            "",
            f"- Clean selected-win cases found: `{len(rows)}`",
            "",
        ]
        for case in rows[:5]:
            lines += [
                f"### source_idx `{case['source_idx']}`, selected variant `{case['selected_variant_idx']}`",
                "",
                f"- target: `{case['target']}`",
                f"- original v0 prediction: `{case['original_prediction']}`",
                f"- SID-selected prediction: `{case['selected_prediction']}`",
                f"- English source: {short(case['english_question'])}",
                f"- Original v0: {short(case['original_question'])}",
                f"- SID-selected: {short(case['selected_question'])}",
                "",
            ]

    json_path = Path("/root/gsm8k_sid_clean_selected_win_cases.json")
    md_path = Path("/root/gsm8k_sid_clean_selected_win_cases.md")
    json_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
