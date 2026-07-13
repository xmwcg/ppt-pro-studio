#!/usr/bin/env python3
"""Prompt enhancement helper (P3-2).

Turns rough intent into a structured brief scaffold with a chosen narrative
structure and delivery path. Deterministic + offline; meant as a starting
point the AI agent (Prompt Refiner methodology) then refines into a full
`brief.json`. Mirrors `references/prompt-refiner-PROMPT.md`.

Usage:
    python3 scripts/prompt_enhance.py --topic "AI 投资机遇" --audience investor \
        --goal persuade --narrative persuade --delivery showcase --theme tech_dark \
        --length 12 [--out brief.json]

Exit 0 on success; prints the scaffold JSON to stdout (or writes --out).
"""
from __future__ import annotations

import argparse
import json
import sys

# Narrative skeleton -> ordered list of (type, purpose). `type` maps to the
# renderer used in step ②->③ of the pipeline (see SKILL.md).
NARRATIVE_SKELETONS: dict[str, list[tuple[str, str]]] = {
    "persuade": [
        ("cover", "封面 + 一句话价值主张"),
        ("section", "痛点：现状为什么痛"),
        ("content", "为什么是现在（趋势/窗口）"),
        ("content", "我们的方案（核心差异）"),
        ("media", "证明：数据 / 案例 / 客户 logos"),
        ("chart", "价值 / ROI 量化"),
        ("summary", "行动号召 CTA（试用 / 投资 / 合作）"),
    ],
    "inform": [
        ("cover", "封面 + 本期主题"),
        ("agenda", "议程"),
        ("content", "背景 / 目标"),
        ("chart", "关键进展（数据）"),
        ("two_column", "问题分析（左因 / 右果）"),
        ("summary", "结论"),
        ("contact", "下一步 / 负责人"),
    ],
    "teach": [
        ("cover", "封面 + 课程名"),
        ("section", "学习目标"),
        ("content", "核心概念"),
        ("content", "原理解析"),
        ("media", "实战案例"),
        ("two_column", "随堂练习（左题 / 右思路）"),
        ("summary", "小结 + 拓展阅读"),
    ],
    "inspire": [
        ("cover", "封面 + 使命金句"),
        ("quote", "愿景 / 使命"),
        ("content", "共鸣故事"),
        ("section", "挑战 / 机遇"),
        ("content", "我们的行动"),
        ("summary", "邀请同行（号召）"),
        ("contact", "加入方式"),
    ],
}

VALID_NARRATIVES = list(NARRATIVE_SKELETONS.keys())
VALID_DELIVERY = ("editable", "showcase")
VALID_THEMES = (
    "tech_dark", "business_blue", "creative_purple", "academic_white",
    "minimal_gray", "fintech_green", "sunset_orange", "mono_ink",
)


def build_scaffold(args: argparse.Namespace) -> dict:
    skeleton = NARRATIVE_SKELETONS[args.narrative]
    outline = [
        {"type": t, "purpose": p, "title": ""} for t, p in skeleton
    ]
    # Trim/pad outline to requested length is left to the agent; scaffold keeps
    # the narrative's natural shape but records the target length.
    return {
        "topic": args.topic,
        "audience": args.audience,
        "goal": args.goal,
        "narrative": args.narrative,
        "delivery": args.delivery,
        "theme": args.theme,
        "length": args.length,
        "sections": max(3, min(6, args.length // 2)),
        "constraints": "",
        "acceptance": "可编辑/无水印/中文正常" if args.delivery == "editable"
                      else "视觉震撼、适合演示/路演",
        "outline": outline,
        "pages": [],  # filled by the agent in step ②->③
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a PPT brief from intent.")
    ap.add_argument("--topic", required=True, help="一句话核心命题")
    ap.add_argument("--audience", default="", help="受众（投资人/学员/客户/内部团队）")
    ap.add_argument("--goal", default="", help="目标（说服/教学/汇报/销售）")
    ap.add_argument("--narrative", choices=VALID_NARRATIVES, default="inform",
                    help="叙事骨架")
    ap.add_argument("--delivery", choices=VALID_DELIVERY, default="editable",
                    help="editable=核心引擎可编辑PPTX; showcase=Marp视觉天花板HTML")
    ap.add_argument("--theme", choices=VALID_THEMES, default="tech_dark",
                    help="主题市场调色板")
    ap.add_argument("--length", type=int, default=12, help="目标页数 8-20")
    ap.add_argument("--out", default=None, help="写出 JSON 路径（默认 stdout）")
    args = ap.parse_args()

    scaffold = build_scaffold(args)
    text = json.dumps(scaffold, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"brief scaffold -> {args.out} ({len(scaffold['outline'])} outline pages, "
              f"delivery={args.delivery}, narrative={args.narrative})", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
