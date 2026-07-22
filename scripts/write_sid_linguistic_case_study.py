#!/usr/bin/env python3
import json
from pathlib import Path


RAW = Path("/root/gsm8k_sid_surface_case_study.json")
OUT = Path("/root/gsm8k_sid_linguistic_patterns_with_zh.md")


ZH_NOTES = {
    "npi_Deva": {
        "pattern": "更像标准数学应用题：先给数量和单位，再用「如果/求」式问句收束；数字关系集中，少重复。",
        "glosses": [
            "理查德的楼有 15 层，每层 8 个单元，其中 3/4 已被占用，求空单元数。",
            "吉恩有 30 个棒棒糖，吃掉 2 个，剩下的每 2 个装一袋，问能装满几袋。",
            "篮子里有 25 个橙子，1 个坏了，20% 未熟，2 个酸，求好的橙子数。",
        ],
    },
    "sin_Sinh": {
        "pattern": "偏好显式条件句和总量问句：常见「如果 X，每个/每天 Y，那么总共多少」结构，句子比 miss bucket 更短、更少重复。",
        "glosses": [
            "如果 James 每次冲刺 60 米，每周做 3 次、每次 3 组，问一周总共跑多少米。",
            "Terry 每天吃 2 个酸奶，商店 4 个酸奶卖 5 美元，问 30 天花多少钱。",
            "Jean 有 30 个棒棒糖，吃掉 2 个后，每袋装 2 个，问可以装几袋。",
        ],
    },
    "som_Latn": {
        "pattern": "偏好多商品/多数量的清晰枚举：价格、数量、折扣和总价用较固定的顺序表达，减少长重复从句。",
        "glosses": [
            "Kyle 以 19.50 美元买了一本畅销书，这相当于原价打 25% 折，求原价或折扣关系。",
            "Mishka 买 3 条短裤、3 条裤子、3 双鞋，单价分别是 16.50、22.50、42 美元，求总花费。",
            "Raymond 有 40 颗宝石，Aaron 是它的一半再加 5，Siobhan 比 Aaron 少 2，求 Siobhan 的宝石数。",
        ],
    },
    "swh_Latn": {
        "pattern": "Swahili 的高分 bucket 更像「单位价格 + 数量 + 总额」的规整题面，粗粒度长度/英文比例差异不大，但例子常有清楚的单位词和费用结构。",
        "glosses": [
            "Mishka 买 3 条短裤、3 条裤子、3 双鞋，分别给出每双/每条价格，求总花费。",
            "Candice 原有 80 张便签，又买了一包；工作时给 220 个杯子各贴一张，最后剩 23 张，求新买的一包有多少张。",
            "野餐中成年恐龙每只吃 10 磅土豆沙拉，幼年恐龙吃 5 磅；给定数量后求总需求。",
        ],
    },
    "yor_Latn": {
        "pattern": "偏好数字锚点更明确、重复更少的 Yoruba 题面；常见「卖出数量 × 单价」「买入数量 × 单价」「总共多少」结构。",
        "glosses": [
            "Stephen 有 40 美元基础费用，又加 25%、3 美元和 4 美元，求最终金额。",
            "Tommy 卖出 43 个 brownie，每个 3 美元，又卖出 23 片 cheesecake，每片 4 美元，求总收入。",
            "T-Rex 聚餐中，成年恐龙吃 10 磅，幼年恐龙吃一半；给定成年和幼年数量，求总沙拉重量。",
        ],
    },
    "zul_Latn": {
        "pattern": "偏好简洁条件句和单位/价格结构：句子短，数字和单位靠近，减少机器翻译产生的混合语和重复。",
        "glosses": [
            "James 每次冲刺 60 米，每周 3 次、每次 3 组，问一周总距离。",
            "Kylar 买 16 个玻璃杯，每个 5 美元，每第二个只按 60% 价格，求总价。",
            "Toula 买 3 打甜甜圈、2 打迷你纸杯蛋糕、6 打迷你芝士蛋糕，分别给出每打价格，求总支出。",
        ],
    },
}


def short(s: str, n: int = 320) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def pick_examples(case: dict, lang: str) -> list[dict]:
    examples = [e for e in case["examples"] if e.get("correct")]
    # Prefer examples with multiple numbers and not too much truncation.
    examples = sorted(
        examples,
        key=lambda e: (
            -sum(ch.isdigit() for ch in str(e.get("question", ""))),
            len(str(e.get("question", ""))),
        ),
    )
    picked = []
    glosses = ZH_NOTES[lang]["glosses"]
    for idx, ex in enumerate(examples[:3]):
        item = dict(ex)
        item["zh_gloss"] = glosses[min(idx, len(glosses) - 1)]
        picked.append(item)
    return picked


def main() -> None:
    data = json.loads(RAW.read_text(encoding="utf-8"))
    lines = [
        "# SID Linguistic Pattern Case Study",
        "",
        "This report avoids treating SID selection as merely repairing corrupted translations. Instead, it looks for recurring lexical and syntactic patterns in high-uplift SID buckets.",
        "Each non-English example includes a concise Chinese gloss for paper drafting.",
        "",
        "## Summary Table",
        "",
        "| lang | representative SID | test hit vs miss | linguistic pattern |",
        "| --- | --- | ---: | --- |",
    ]
    for res in data:
        lang = res["lang"]
        case = res["top_rule_cases"][0]
        r = case["rule"]
        lines.append(
            f"| {lang} | L{r['layer']}-K{r['level']}-SID{r['sid']} | "
            f"{case['test_hit_accuracy']:.3f} vs {case['test_miss_accuracy']:.3f} | "
            f"{ZH_NOTES[lang]['pattern']} |"
        )

    lines += [
        "",
        "## Detailed Cases",
        "",
    ]
    for res in data:
        lang = res["lang"]
        case = res["top_rule_cases"][0]
        r = case["rule"]
        fm = case["feature_means"]
        lines += [
            f"### {lang}: L{r['layer']}-K{r['level']}-SID{r['sid']}",
            "",
            f"- Test hit accuracy: `{case['test_hit_accuracy']:.3f}`; miss accuracy: `{case['test_miss_accuracy']:.3f}`.",
            f"- Coarse features: tokens hit/miss `{fm['hit_tokens']:.1f}/{fm['miss_tokens']:.1f}`, number count `{fm['hit_num_count']:.1f}/{fm['miss_num_count']:.1f}`, max repeated-token run `{fm['hit_max_token_run']:.1f}/{fm['miss_max_token_run']:.1f}`.",
            f"- Linguistic reading: {ZH_NOTES[lang]['pattern']}",
            "",
        ]
        for i, ex in enumerate(pick_examples(case, lang), 1):
            lines += [
                f"#### Example {i}",
                "",
                f"- Variant: `{ex['variant_id']}`; prediction `{ex['relaxed_prediction']}`; target `{ex['target']}`.",
                f"- Original surface form: {short(ex['question'])}",
                f"- 中文意译: {ex['zh_gloss']}",
                "",
            ]

    lines += [
        "## Paper-Friendly Interpretation",
        "",
        "The SID buckets appear to capture surface-form regimes that are friendlier to the solver: compact condition clauses, explicit numeric anchors, unit/price expressions placed close to their quantities, and direct total/count questions. These are linguistic regularities, not just translation-error repairs.",
        "",
        "A careful claim would be: high-uplift SIDs partially align with interpretable surface-form properties, while still retaining latent information beyond simple length or number-count features.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
