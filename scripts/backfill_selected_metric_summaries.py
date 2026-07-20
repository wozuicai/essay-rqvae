#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import pandas as pd


BASE = Path("/root/gsm8k_single_language_experiment")
LANGS = ["swh_Latn", "yor_Latn", "som_Latn"]


def summarize(name: str, df: pd.DataFrame) -> dict:
    n = int(len(df))
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


def attach_selection_metrics(out: Path, selection_rel: str, out_rel: str):
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
    eval_metrics = eval_df[metric_cols].copy()
    sel = pd.read_parquet(out / selection_rel)
    merged = sel.merge(
        eval_metrics,
        left_on="selected_variant_row",
        right_on="variant_row",
        how="left",
        validate="one_to_one",
    )
    if merged["strict_correct"].isna().any():
        raise RuntimeError(f"missing eval metrics for {out / selection_rel}")
    pq = out / out_rel
    csv = pq.with_suffix(".csv")
    merged.to_parquet(pq, index=False)
    merged.to_csv(csv, index=False)
    return merged, pq, csv


def backfill(lang: str) -> dict:
    out = BASE / lang
    eval_df = pd.read_parquet(out / "eval/eval_results.parquet")
    test_all = eval_df[eval_df["split"] == "test"].copy()
    test_original = test_all[test_all["variant_idx"] == 0].copy()

    sid_sel, sid_pq, sid_csv = attach_selection_metrics(
        out,
        "analysis/test_selection.parquet",
        "analysis/test_selection_with_eval_metrics.parquet",
    )
    lgbm_sel, lgbm_pq, lgbm_csv = attach_selection_metrics(
        out,
        "analysis_lgbm/test_selection_lgbm.parquet",
        "analysis_lgbm/test_selection_lgbm_with_eval_metrics.parquet",
    )
    lgbm0_sel, lgbm0_pq, lgbm0_csv = attach_selection_metrics(
        out,
        "analysis_lgbm_no_level0/test_selection_lgbm.parquet",
        "analysis_lgbm_no_level0/test_selection_lgbm_with_eval_metrics.parquet",
    )

    rows = [
        summarize("all_test_variants_average", test_all),
        summarize("original_variant_v0", test_original),
        summarize("sid_rules_selected", sid_sel),
        summarize("lgbm_all_levels_selected", lgbm_sel),
        summarize("lgbm_exclude_level0_selected", lgbm0_sel),
    ]
    summary = {
        "created_at": pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S UTC"),
        "lang": lang,
        "metrics": rows,
        "detail_files": {
            "eval_results": str(out / "eval/eval_results.parquet"),
            "sid_rules_selected": str(sid_pq),
            "sid_rules_selected_csv": str(sid_csv),
            "lgbm_all_levels_selected": str(lgbm_pq),
            "lgbm_all_levels_selected_csv": str(lgbm_csv),
            "lgbm_exclude_level0_selected": str(lgbm0_pq),
            "lgbm_exclude_level0_selected_csv": str(lgbm0_csv),
        },
    }

    json_path = out / "eval/test_selected_metric_summary.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md = [
        f"# {lang} Test Metric Comparison",
        "",
        "| setting | n | strict acc | strict correct | relaxed acc | relaxed correct | strict-else-relaxed acc | strict-else-relaxed correct |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        md.append(
            f"| {row['setting']} | {row['n']} | {row['strict_accuracy']:.12f} | {row['strict_correct']} | "
            f"{row['relaxed_last_number_accuracy']:.12f} | {row['relaxed_correct']} | "
            f"{row['strict_else_relaxed_accuracy']:.12f} | {row['strict_else_relaxed_correct']} |"
        )
    md.extend(
        [
            "",
            "Detail files:",
            f"- `{sid_pq}`",
            f"- `{lgbm_pq}`",
            f"- `{lgbm0_pq}`",
            f"- `{json_path}`",
        ]
    )
    md_path = out / "eval/test_selected_metric_comparison.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    return {
        "lang": lang,
        "summary": str(json_path),
        "markdown": str(md_path),
        "metrics": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=LANGS)
    args = ap.parse_args()
    results = [backfill(lang) for lang in args.langs]
    print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
