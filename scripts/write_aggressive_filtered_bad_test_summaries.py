#!/usr/bin/env python3
import json
import re
from pathlib import Path

import pandas as pd


BASE = Path("/root/gsm8k_single_language_experiment")
QUALITY_AUDIT = Path("/root/gsm8k_nllb_direct_quality_audit.json")
LANGS = ["npi_Deva", "sin_Sinh", "som_Latn", "swh_Latn", "yor_Latn", "zul_Latn"]

DIGIT_CHARS = "0-9०१२۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹"
BRACKET_P_ANY_RE = re.compile(rf"\[\s*P\s*[{DIGIT_CHARS}]*\s*\]", re.IGNORECASE)
UNLABELED_DIGIT_RE = re.compile(rf"\[\s*[{DIGIT_CHARS}]+\s*\]")
PAGE_MARKER_RE = re.compile(
    r"\[[^\]]*(?:page|página|පිටුව|पृष्ठ|ገጽ|စာမျက်နှာ|ទំព័រ|ຫນ້າ|"
    r"صفحة|shafi|ukurasa|iwe|oju|ikhasi)[^\]]*\]",
    re.IGNORECASE,
)
ONLY_NUM_PUNCT_RE = re.compile(rf"^[\s{DIGIT_CHARS}.,/%$+\-*=<>#\[\]Pp]+$")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize(name: str, df: pd.DataFrame) -> dict:
    n = int(len(df))
    if n == 0:
        return {
            "setting": name,
            "n": 0,
            "strict_accuracy": None,
            "strict_correct": 0,
            "relaxed_last_number_accuracy": None,
            "relaxed_correct": 0,
            "strict_else_relaxed_accuracy": None,
            "strict_else_relaxed_correct": 0,
        }
    return {
        "setting": name,
        "n": n,
        "strict_accuracy": float(df["strict_correct"].mean()),
        "strict_correct": int(df["strict_correct"].sum()),
        "relaxed_last_number_accuracy": float(df["relaxed_correct"].mean()),
        "relaxed_correct": int(df["relaxed_correct"].sum()),
        "strict_else_relaxed_accuracy": float(df["strict_else_relaxed_correct"].mean()),
        "strict_else_relaxed_correct": int(df["strict_else_relaxed_correct"].sum()),
    }


def question_reasons(question: str) -> list[str]:
    q = str(question or "").strip()
    reasons = []
    if not q:
        reasons.append("empty_question")
    if BRACKET_P_ANY_RE.search(q):
        reasons.append("placeholder_P_in_question")
    if UNLABELED_DIGIT_RE.search(q):
        reasons.append("unlabeled_digit_placeholder_in_question")
    if PAGE_MARKER_RE.search(q):
        reasons.append("page_marker_in_question")
    if ONLY_NUM_PUNCT_RE.fullmatch(q) if q else True:
        reasons.append("numeric_or_placeholder_only_question")
    if len(q.split()) <= 3 and re.search(r"\d|[०-९]", q):
        reasons.append("very_short_numeric_question")
    if len(BRACKET_P_ANY_RE.findall(q)) >= 3:
        reasons.append("many_placeholder_P_in_question")
    if len(UNLABELED_DIGIT_RE.findall(q)) >= 3:
        reasons.append("many_unlabeled_digit_placeholders_in_question")
    return sorted(set(reasons))


def audit_bad_keys(lang: str) -> dict[int, set[str]]:
    if not QUALITY_AUDIT.exists():
        return {}
    data = json.loads(QUALITY_AUDIT.read_text(encoding="utf-8"))
    examples = data.get("examples", {}).get(lang, {})
    keys: dict[int, set[str]] = {}
    for reason in [
        "bracket_p_any",
        "repeated_bracket_p_question",
        "only_num_punct_question",
        "short_question_le_3_words",
        "page_marker_in_question",
    ]:
        for row in examples.get(reason, []):
            if row.get("config") == "main" and row.get("split") == "test":
                keys.setdefault(int(row["idx"]), set()).add(f"quality_audit:{reason}")
    return keys


def attach_selection_metrics(out: Path, selection_rel: str) -> pd.DataFrame:
    eval_df = pd.read_parquet(out / "eval/eval_results.parquet")
    metric_cols = [
        "variant_row",
        "variant_id",
        "split",
        "source_idx",
        "variant_idx",
        "target",
        "strict_prediction",
        "relaxed_prediction",
        "strict_else_relaxed_prediction",
        "strict_correct",
        "relaxed_correct",
        "strict_else_relaxed_correct",
        "correct",
    ]
    sel = pd.read_parquet(out / selection_rel)
    merged = sel.merge(
        eval_df[metric_cols],
        left_on="selected_variant_row",
        right_on="variant_row",
        how="left",
        suffixes=("", "_eval"),
        validate="one_to_one",
    )
    if merged["strict_correct"].isna().any():
        raise RuntimeError(f"missing eval metrics for {out / selection_rel}")
    return merged


def filtered_summary_for_lang(lang: str) -> dict:
    out = BASE / lang
    source_df = pd.read_parquet(out / "source.parquet")
    test_source = source_df[source_df["split"] == "test"].copy()
    audit_keys = audit_bad_keys(lang)

    bad_rows = []
    for row in test_source.to_dict("records"):
        source_idx = int(row["source_idx"])
        reasons = set(question_reasons(str(row["question"])))
        reasons.update(audit_keys.get(source_idx, set()))
        if reasons:
            bad_rows.append(
                {
                    "split": str(row["split"]),
                    "source_idx": source_idx,
                    "reasons": ";".join(sorted(reasons)),
                    "question": str(row["question"]),
                    "answer": str(row["answer"]),
                    "target": row.get("target"),
                }
            )
    bad_df = pd.DataFrame(bad_rows)
    bad_keys = set(int(r["source_idx"]) for r in bad_rows)

    eval_df = pd.read_parquet(out / "eval/eval_results.parquet")
    test_all = eval_df[eval_df["split"] == "test"].copy()
    filtered_test_all = test_all[~test_all["source_idx"].astype(int).isin(bad_keys)].copy()
    filtered_original = filtered_test_all[filtered_test_all["variant_idx"] == 0].copy()

    sid_sel = attach_selection_metrics(out, "analysis/test_selection.parquet")
    lgbm_sel = attach_selection_metrics(out, "analysis_lgbm/test_selection_lgbm.parquet")
    lgbm0_sel = attach_selection_metrics(out, "analysis_lgbm_no_level0/test_selection_lgbm.parquet")
    sid_sel_f = sid_sel[~sid_sel["source_idx"].astype(int).isin(bad_keys)].copy()
    lgbm_sel_f = lgbm_sel[~lgbm_sel["source_idx"].astype(int).isin(bad_keys)].copy()
    lgbm0_sel_f = lgbm0_sel[~lgbm0_sel["source_idx"].astype(int).isin(bad_keys)].copy()

    rows = [
        summarize("all_test_variants_average_aggressive_filtered", filtered_test_all),
        summarize("original_variant_v0_aggressive_filtered", filtered_original),
        summarize("sid_rules_selected_aggressive_filtered", sid_sel_f),
        summarize("lgbm_all_levels_selected_aggressive_filtered", lgbm_sel_f),
        summarize("lgbm_exclude_level0_selected_aggressive_filtered", lgbm0_sel_f),
    ]

    eval_dir = out / "eval"
    bad_json = eval_dir / "test_bad_source_rows_for_aggressive_filtered_summary.json"
    bad_csv = eval_dir / "test_bad_source_rows_for_aggressive_filtered_summary.csv"
    summary_json = eval_dir / "test_aggressive_filtered_bad_source_metric_summary.json"
    summary_md = eval_dir / "test_aggressive_filtered_bad_source_metric_comparison.md"

    write_json(bad_json, bad_rows)
    if len(bad_df):
        bad_df.to_csv(bad_csv, index=False)
    else:
        pd.DataFrame(columns=["split", "source_idx", "reasons", "question", "answer", "target"]).to_csv(
            bad_csv, index=False
        )

    summary = {
        "lang": lang,
        "filter_definition": {
            "scope": "test source rows only",
            "mode": "aggressive",
            "dropped_source_rows": int(len(bad_keys)),
            "kept_source_rows": int(len(test_source) - len(bad_keys)),
            "rules": [
                "placeholder_P_in_question",
                "unlabeled_digit_placeholder_in_question",
                "page_marker_in_question",
                "numeric_or_placeholder_only_question",
                "very_short_numeric_question",
                "many_placeholder_P_in_question",
                "many_unlabeled_digit_placeholders_in_question",
                "quality_audit example rows from /root/gsm8k_nllb_direct_quality_audit.json",
            ],
        },
        "metrics": rows,
        "detail_files": {
            "bad_source_rows_json": str(bad_json),
            "bad_source_rows_csv": str(bad_csv),
            "summary_markdown": str(summary_md),
            "eval_results": str(out / "eval/eval_results.parquet"),
        },
    }
    write_json(summary_json, summary)

    md = [
        f"# {lang} Aggressive Filtered Test Metric Comparison",
        "",
        "This report excludes aggressive high-risk bad `test` source rows only. Original result files are not modified.",
        "",
        f"- Dropped source rows: `{len(bad_keys)}` / `{len(test_source)}`",
        f"- Kept source rows: `{len(test_source) - len(bad_keys)}` / `{len(test_source)}`",
        f"- Bad-row details: `{bad_json}`",
        "",
        "| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        md.append(
            f"| {row['setting']} | {row['n']} | "
            f"{row['strict_accuracy'] if row['strict_accuracy'] is not None else 'NA'} | {row['strict_correct']} | "
            f"{row['relaxed_last_number_accuracy'] if row['relaxed_last_number_accuracy'] is not None else 'NA'} | {row['relaxed_correct']} | "
            f"{row['strict_else_relaxed_accuracy'] if row['strict_else_relaxed_accuracy'] is not None else 'NA'} | {row['strict_else_relaxed_correct']} |"
        )
    summary_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"lang": lang, "dropped": len(bad_keys), "kept": len(test_source) - len(bad_keys), "metrics": rows}


def main() -> None:
    results = [filtered_summary_for_lang(lang) for lang in LANGS]
    out_json = Path("/root/gsm8k_aggressive_filtered_bad_test_summary_all.json")
    out_md = Path("/root/gsm8k_aggressive_filtered_bad_test_summary_all.md")
    write_json(out_json, results)

    md = [
        "# Aggressive Filtered Bad-Test-Row Summary",
        "",
        "Derived summaries only. Original experiment result files were not modified.",
        "",
        "| lang | dropped test source rows | kept test source rows | original v0 strict | original v0 strict-else-relaxed | SID strict-else-relaxed | LightGBM strict-else-relaxed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in results:
        by_name = {m["setting"]: m for m in r["metrics"]}
        original = by_name["original_variant_v0_aggressive_filtered"]
        sid = by_name["sid_rules_selected_aggressive_filtered"]
        lgbm = by_name["lgbm_all_levels_selected_aggressive_filtered"]
        md.append(
            f"| {r['lang']} | {r['dropped']} | {r['kept']} | "
            f"{original['strict_accuracy']} | {original['strict_else_relaxed_accuracy']} | "
            f"{sid['strict_else_relaxed_accuracy']} | {lgbm['strict_else_relaxed_accuracy']} |"
        )
    md += ["", "Per-language files:"]
    for lang in LANGS:
        md.append(f"- `/root/gsm8k_single_language_experiment/{lang}/eval/test_aggressive_filtered_bad_source_metric_summary.json`")
        md.append(f"- `/root/gsm8k_single_language_experiment/{lang}/eval/test_bad_source_rows_for_aggressive_filtered_summary.csv`")
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
