#!/usr/bin/env python3
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path("/root/gsm8k_single_language_experiment")
LANGS = ["npi_Deva", "sin_Sinh", "som_Latn", "swh_Latn", "yor_Latn", "zul_Latn"]

DIGIT_RE = re.compile(r"\$?\d+(?:,\d{3})*(?:\.\d+)?(?:/\d+)?%?")
ASCII_WORD_RE = re.compile(r"\b[A-Za-z]{3,}\b")
PLACEHOLDER_RE = re.compile(r"\[\s*P\s*\]|\[\s*P\s*\d+\s*\]|\[\s*\d+\s*\]", re.IGNORECASE)
PAGE_RE = re.compile(
    r"\[[^\]]*(?:page|página|පිටුව|पृष्ठ|ገጽ|စာမျက်နှာ|ទំព័រ|ຫນ້າ|"
    r"صفحة|shafi|ukurasa|iwe|oju|ikhasi)[^\]]*\]",
    re.IGNORECASE,
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def max_token_run(text: str) -> int:
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


def surface_features(text: str) -> dict:
    text = str(text or "")
    words = text.split()
    ascii_words = ASCII_WORD_RE.findall(text)
    nums = DIGIT_RE.findall(text)
    return {
        "chars": len(text),
        "tokens": len(words),
        "num_count": len(nums),
        "ascii_word_count": len(ascii_words),
        "ascii_word_rate": len(ascii_words) / max(len(words), 1),
        "placeholder_count": len(PLACEHOLDER_RE.findall(text)),
        "page_marker": bool(PAGE_RE.search(text)),
        "max_token_run": max_token_run(text),
        "question": text,
    }


def short(text: str, n: int = 220) -> str:
    s = " ".join(str(text).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def load_lang(lang: str):
    out = BASE / lang
    variants = pd.read_parquet(out / "variants/variants.parquet")
    eval_df = pd.read_parquet(out / "eval/eval_results.parquet")
    merged = variants.merge(
        eval_df[
            [
                "variant_row",
                "strict_correct",
                "relaxed_correct",
                "strict_else_relaxed_correct",
                "strict_prediction",
                "relaxed_prediction",
            ]
        ],
        on="variant_row",
        how="left",
        validate="one_to_one",
    )
    rules = pd.read_parquet(out / "analysis/significant_sid_rules.parquet")
    meta = read_json(out / "rqvae/sids_meta.json")
    sids = np.memmap(meta["memmap"], dtype=np.uint16, mode="r", shape=tuple(meta["shape"]))
    return out, merged, rules, sids


def rule_examples(merged: pd.DataFrame, sids, rule: dict, split: str = "test") -> dict:
    layer = int(rule["layer"])
    level = int(rule["level"])
    sid = int(rule["sid"])
    split_df = merged[merged["split"] == split].copy()
    row_ids = split_df["variant_row"].to_numpy(dtype=np.int64)
    hit_mask = np.asarray(sids[row_ids, layer, level] == sid)
    hit = split_df[hit_mask].copy()
    miss = split_df[~hit_mask].copy()
    if len(hit) == 0:
        return {}
    hit_features = pd.DataFrame([surface_features(q) for q in hit["question"]])
    miss_features = pd.DataFrame([surface_features(q) for q in miss["question"]])

    def mean(col, df):
        return float(df[col].mean()) if len(df) else None

    by_variant = hit.groupby("variant_idx")["strict_else_relaxed_correct"].agg(["count", "mean"]).reset_index()
    hit_sorted_correct = hit[hit["strict_else_relaxed_correct"]].head(8)
    hit_sorted_wrong = hit[~hit["strict_else_relaxed_correct"]].head(4)

    examples = []
    for _, row in pd.concat([hit_sorted_correct.head(4), hit_sorted_wrong.head(2)]).iterrows():
        examples.append(
            {
                "variant_id": row["variant_id"],
                "source_idx": int(row["source_idx"]),
                "variant_idx": int(row["variant_idx"]),
                "correct": bool(row["strict_else_relaxed_correct"]),
                "strict_prediction": row.get("strict_prediction"),
                "relaxed_prediction": row.get("relaxed_prediction"),
                "target": row.get("target"),
                "question": short(row["question"], 350),
            }
        )

    return {
        "rule": {
            "layer": layer,
            "level": level,
            "sid": sid,
            "train_n": int(rule["n"]),
            "train_accuracy": float(rule["accuracy"]),
            "train_uplift": float(rule["uplift"]),
            "q_value": float(rule["q_value"]),
        },
        "test_hit_n": int(len(hit)),
        "test_hit_accuracy": float(hit["strict_else_relaxed_correct"].mean()),
        "test_miss_accuracy": float(miss["strict_else_relaxed_correct"].mean()) if len(miss) else None,
        "feature_means": {
            "hit_tokens": mean("tokens", hit_features),
            "miss_tokens": mean("tokens", miss_features),
            "hit_num_count": mean("num_count", hit_features),
            "miss_num_count": mean("num_count", miss_features),
            "hit_ascii_word_rate": mean("ascii_word_rate", hit_features),
            "miss_ascii_word_rate": mean("ascii_word_rate", miss_features),
            "hit_placeholder_count": mean("placeholder_count", hit_features),
            "miss_placeholder_count": mean("placeholder_count", miss_features),
            "hit_max_token_run": mean("max_token_run", hit_features),
            "miss_max_token_run": mean("max_token_run", miss_features),
        },
        "variant_distribution": by_variant.to_dict("records"),
        "examples": examples,
    }


def language_cases(lang: str) -> dict:
    out, merged, rules, sids = load_lang(lang)
    rules = rules.sort_values(["uplift", "n"], ascending=[False, False]).reset_index(drop=True)
    # Keep rules that have enough training support and are not trivially tiny.
    candidates = rules[rules["n"] >= 500].head(25).to_dict("records")
    case_records = []
    seen = set()
    for rule in candidates:
        key = (int(rule["layer"]), int(rule["level"]), int(rule["sid"]))
        if key in seen:
            continue
        rec = rule_examples(merged, sids, rule, split="test")
        if not rec:
            continue
        if rec["test_hit_n"] < 80:
            continue
        case_records.append(rec)
        seen.add(key)
        if len(case_records) >= 6:
            break

    # Selected-vs-original illustrative source-level wins.
    selection = pd.read_parquet(out / "analysis/test_selection_with_eval_metrics.parquet")
    test = merged[merged["split"] == "test"].copy()
    original = test[test["variant_idx"] == 0][
        ["source_idx", "variant_row", "variant_idx", "question", "strict_else_relaxed_correct"]
    ].rename(
        columns={
            "variant_row": "original_variant_row",
            "variant_idx": "original_variant_idx",
            "question": "original_question",
            "strict_else_relaxed_correct": "original_correct",
        }
    )
    if "source_idx" not in selection.columns and "source_idx_x" in selection.columns:
        selection = selection.rename(columns={"source_idx_x": "source_idx"})
    selected = selection.merge(original, on="source_idx", how="left")
    wins = selected[
        (selected["original_correct"] == False)
        & (selected["strict_else_relaxed_correct"] == True)
        & (selected["selected_variant_idx"] != 0)
    ].head(8)
    win_cases = []
    for _, row in wins.iterrows():
        sel_question = test.loc[test["variant_row"] == int(row["selected_variant_row"]), "question"].iloc[0]
        win_cases.append(
            {
                "source_idx": int(row["source_idx"]),
                "selected_variant_idx": int(row["selected_variant_idx"]),
                "original_question": short(row["original_question"], 280),
                "selected_question": short(sel_question, 280),
                "target": row.get("target"),
                "selected_prediction": row.get("strict_else_relaxed_prediction"),
            }
        )

    return {
        "lang": lang,
        "analysis_summary": read_json(out / "analysis/analysis_summary.json"),
        "top_rule_cases": case_records,
        "selected_over_original_cases": win_cases,
    }


def write_markdown(results: list[dict], path: Path) -> None:
    lines = [
        "# SID Surface-Form Case Study",
        "",
        "This report inspects whether high-uplift SID buckets correspond to visible question-surface patterns.",
        "All statistics are computed from existing `variants.parquet`, `eval_results.parquet`, `sids.uint16.memmap`, and `significant_sid_rules.parquet`; no model was rerun.",
        "",
        "Interpretation note: SID rules were learned on train variants. The case descriptions below are qualitative and should be used as examples, not as independent significance claims.",
        "",
        "## Cross-Language Summary",
        "",
        "| lang | train baseline | test original | test SID selected | significant rules | qualitative pattern |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for res in results:
        s = res["analysis_summary"]
        patterns = []
        for c in res["top_rule_cases"][:3]:
            fm = c["feature_means"]
            if (fm["hit_ascii_word_rate"] or 0) > (fm["miss_ascii_word_rate"] or 0) + 0.05:
                patterns.append("more English/Latin residue")
            if (fm["hit_tokens"] or 0) < (fm["miss_tokens"] or 0) - 4:
                patterns.append("shorter prompts")
            if (fm["hit_num_count"] or 0) > (fm["miss_num_count"] or 0) + 0.5:
                patterns.append("more explicit numbers")
            if not patterns:
                patterns.append("latent bucket not obvious from coarse features")
        pattern_text = "; ".join(dict.fromkeys(patterns))
        lines.append(
            f"| {res['lang']} | {s['baseline_train_accuracy']:.4f} | {s['test_original_accuracy']:.4f} | "
            f"{s['test_selected_accuracy']:.4f} | {s['num_significant_rules']} | {pattern_text} |"
        )

    for res in results:
        lines += [
            "",
            f"## {res['lang']}",
            "",
            "### High-Uplift SID Buckets",
            "",
        ]
        for idx, c in enumerate(res["top_rule_cases"][:4], 1):
            r = c["rule"]
            fm = c["feature_means"]
            lines += [
                f"#### Case {idx}: layer {r['layer']} / level {r['level']} / sid {r['sid']}",
                "",
                f"- Train bucket: n={r['train_n']}, accuracy={r['train_accuracy']:.4f}, uplift={r['train_uplift']:.4f}, q={r['q_value']:.2e}",
                f"- Test hit: n={c['test_hit_n']}, strict-else-relaxed accuracy={c['test_hit_accuracy']:.4f}; miss accuracy={c['test_miss_accuracy']:.4f}",
                f"- Surface means: tokens hit/miss={fm['hit_tokens']:.1f}/{fm['miss_tokens']:.1f}; numbers hit/miss={fm['hit_num_count']:.1f}/{fm['miss_num_count']:.1f}; ascii-word-rate hit/miss={fm['hit_ascii_word_rate']:.3f}/{fm['miss_ascii_word_rate']:.3f}; max repeated-token run hit/miss={fm['hit_max_token_run']:.1f}/{fm['miss_max_token_run']:.1f}",
                "- Variant distribution in this bucket:",
                "",
                "| variant_idx | count | accuracy |",
                "| ---: | ---: | ---: |",
            ]
            for row in c["variant_distribution"]:
                lines.append(f"| {int(row['variant_idx'])} | {int(row['count'])} | {float(row['mean']):.4f} |")
            lines += ["", "- Representative hit examples:", ""]
            for ex in c["examples"][:4]:
                mark = "correct" if ex["correct"] else "wrong"
                lines.append(
                    f"  - `{ex['variant_id']}` ({mark}, pred={ex['relaxed_prediction']}, target={ex['target']}): {ex['question']}"
                )
            lines.append("")

        lines += [
            "### Source-Level Cases Where SID Selection Fixes Original v0",
            "",
        ]
        if not res["selected_over_original_cases"]:
            lines.append("- No compact examples found under the simple extraction criterion.")
        for ex in res["selected_over_original_cases"][:5]:
            lines += [
                f"- source_idx `{ex['source_idx']}`, selected variant `{ex['selected_variant_idx']}`, target `{ex['target']}`, selected pred `{ex['selected_prediction']}`",
                f"  - Original v0: {ex['original_question']}",
                f"  - Selected: {ex['selected_question']}",
            ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    results = [language_cases(lang) for lang in LANGS]
    json_path = Path("/root/gsm8k_sid_surface_case_study.json")
    md_path = Path("/root/gsm8k_sid_surface_case_study.md")
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(results, md_path)
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
