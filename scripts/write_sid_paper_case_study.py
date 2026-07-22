#!/usr/bin/env python3
import json
from pathlib import Path


RAW = Path("/root/gsm8k_sid_surface_case_study.json")
OUT = Path("/root/gsm8k_sid_surface_paper_cases.md")


def short(s: str, n: int = 260) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def pattern_sentence(lang: str, case: dict) -> str:
    fm = case["feature_means"]
    hit_tokens = fm["hit_tokens"]
    miss_tokens = fm["miss_tokens"]
    hit_nums = fm["hit_num_count"]
    miss_nums = fm["miss_num_count"]
    hit_run = fm["hit_max_token_run"]
    miss_run = fm["miss_max_token_run"]
    parts = []
    if hit_tokens + 3 < miss_tokens:
        parts.append(f"shorter questions ({hit_tokens:.1f} vs {miss_tokens:.1f} tokens)")
    if hit_nums > miss_nums + 0.4:
        parts.append(f"more explicit numeric anchors ({hit_nums:.1f} vs {miss_nums:.1f})")
    if hit_run + 0.5 < miss_run:
        parts.append(f"less repetition (max run {hit_run:.1f} vs {miss_run:.1f})")
    if not parts:
        parts.append("a latent cluster whose coarse lexical features are subtle")
    return "; ".join(parts)


def main() -> None:
    data = json.loads(RAW.read_text(encoding="utf-8"))
    lines = [
        "# SID Surface-Form Paper Cases",
        "",
        "This is a compact, paper-facing version of `/root/gsm8k_sid_surface_case_study.md`.",
        "It highlights cases where high-uplift SID buckets correspond to visible surface-form differences, plus examples where SID selection fixes the original translated question.",
        "",
        "## Main Observation",
        "",
        "Across the six languages, high-uplift SID buckets often correspond to questions that are shorter, less repetitive, and have clearer numeric anchors. This is most visible in low-resource/noisy translations such as Nepali, Sinhala, Yoruba, and Zulu. In Swahili and Somali, the distinction is subtler, but the high-uplift buckets still capture cleaner arithmetic word-problem forms.",
        "",
        "## One Representative SID Bucket Per Language",
        "",
        "| lang | SID rule | train acc/uplift | test hit acc | test miss acc | visible surface pattern |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for res in data:
        best = res["top_rule_cases"][0]
        r = best["rule"]
        lines.append(
            f"| {res['lang']} | L{r['layer']}-K{r['level']}-SID{r['sid']} | "
            f"{r['train_accuracy']:.3f} / +{r['train_uplift']:.3f} | "
            f"{best['test_hit_accuracy']:.3f} | {best['test_miss_accuracy']:.3f} | "
            f"{pattern_sentence(res['lang'], best)} |"
        )

    lines += [
        "",
        "## Language-Level Case Notes",
        "",
    ]

    for res in data:
        lang = res["lang"]
        best = res["top_rule_cases"][0]
        r = best["rule"]
        lines += [
            f"### {lang}",
            "",
            f"Representative high-uplift rule: `layer={r['layer']}, level={r['level']}, sid={r['sid']}`.",
            f"On test variants, this bucket has strict-else-relaxed accuracy `{best['test_hit_accuracy']:.3f}` versus `{best['test_miss_accuracy']:.3f}` outside the bucket.",
            f"Surface pattern: {pattern_sentence(lang, best)}.",
            "",
            "Representative bucket hits:",
            "",
        ]
        for ex in best["examples"][:3]:
            correctness = "correct" if ex["correct"] else "wrong"
            lines.append(
                f"- `{ex['variant_id']}` ({correctness}, pred={ex['relaxed_prediction']}, target={ex['target']}): {short(ex['question'])}"
            )
        lines += ["", "Selection fixes original v0:", ""]
        for ex in res["selected_over_original_cases"][:2]:
            lines += [
                f"- source_idx `{ex['source_idx']}`, selected variant `{ex['selected_variant_idx']}`, target `{ex['target']}`, selected pred `{ex['selected_prediction']}`",
                f"  - Original v0: {short(ex['original_question'])}",
                f"  - SID-selected variant: {short(ex['selected_question'])}",
            ]
        lines.append("")

    lines += [
        "## How To Use In The Paper",
        "",
        "- Use the table above as evidence that SID buckets are not arbitrary labels: many align with shorter, cleaner, less repetitive surface forms.",
        "- Use one or two source-level examples to illustrate the mechanism: the original translation loses or obscures constraints, while the selected variant states the same numbers and relations more explicitly.",
        "- Avoid claiming that every SID is human-interpretable. The safer claim is that high-uplift SID regions partially align with visible surface-form quality, while also capturing latent features not fully explained by simple lexical metrics.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
