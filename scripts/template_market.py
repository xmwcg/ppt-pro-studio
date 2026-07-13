#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
template_market.py — PPT Pro Studio template market (P3-9).

A template is a ready-to-use starting deck: a theme + a narrative + a default
delivery path + a page scaffold (slide types with sample titles). Users pick a
template, then fill/adjust the content. Templates live as standalone JSON under
`templates/` so the catalog is extensible without touching engine code — that is
the "market": browse, pick, extend, and (optionally) sell the source.

CLI:
    python3 template_market.py list                       # print the catalog
    python3 template_market.py show <id>                  # print one template
    python3 template_market.py validate <brief.json>      # is brief's template valid?
    python3 template_market.py init [--dir templates]     # (re)materialize templates/*.json
    python3 template_market.py apply <id> --out brief.json  # scaffold a brief from template

Programmatic:
    from template_market import load_templates, select_template
    TMPL = load_templates(templates_dir)
    t = select_template(brief, TMPL)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical bundled catalog. Also written out as templates/*.json by `init`.
# Each template carries: label, description, theme (a theme_market id),
# narrative (persuade|inform|teach|inspire), delivery (editable|showcase),
# and pages (a scaffold the user fills in).
# ---------------------------------------------------------------------------
BUILTIN_TEMPLATES = {
    "startup_pitch": {
        "label": "融资路演 (Startup Pitch)",
        "description": "投资人路演：痛点→方案→证明→ROI→行动号召",
        "theme": "tech_dark", "narrative": "persuade", "delivery": "editable",
        "pages": [
            {"type": "cover", "title": "公司名 + 一句话价值主张"},
            {"type": "section", "title": "01 痛点"},
            {"type": "content", "title": "现状为什么痛", "items": ["痛点一", "痛点二", "痛点三"]},
            {"type": "content", "title": "为什么是现在", "items": ["趋势/窗口", "催化剂"]},
            {"type": "content", "title": "我们的方案", "items": ["核心差异", "技术壁垒"]},
            {"type": "media", "title": "证明：数据 / 案例 / 客户", "items": ["关键指标", "标杆客户"]},
            {"type": "chart", "title": "价值 / ROI 量化"},
            {"type": "summary", "title": "行动号召（投资 / 合作）"},
        ],
    },
    "course_lecture": {
        "label": "课程课件 (Course Lecture)",
        "description": "培训/教学：目标→概念→原理→案例→练习→小结",
        "theme": "academic_white", "narrative": "teach", "delivery": "editable",
        "pages": [
            {"type": "cover", "title": "课程名"},
            {"type": "section", "title": "学习目标"},
            {"type": "content", "title": "核心概念", "items": ["概念一", "概念二"]},
            {"type": "content", "title": "原理解析", "items": ["原理一", "原理二"]},
            {"type": "media", "title": "实战案例", "items": ["场景", "步骤"]},
            {"type": "two_column", "title": "随堂练习", "items": ["题目", "思路"]},
            {"type": "summary", "title": "小结 + 拓展阅读"},
        ],
    },
    "annual_review": {
        "label": "年度复盘 (Annual Review)",
        "description": "年终汇报：背景→进展→问题→结论→下一步",
        "theme": "business_blue", "narrative": "inform", "delivery": "editable",
        "pages": [
            {"type": "cover", "title": "2025 年度复盘"},
            {"type": "agenda", "title": "议程"},
            {"type": "content", "title": "背景 / 目标"},
            {"type": "chart", "title": "关键进展（数据）"},
            {"type": "two_column", "title": "问题分析", "items": ["原因", "影响"]},
            {"type": "summary", "title": "结论"},
            {"type": "contact", "title": "下一步 / 负责人"},
        ],
    },
    "product_launch": {
        "label": "产品发布 (Product Launch)",
        "description": "发布会/品牌发布：愿景→共鸣→行动→号召（视觉天花板）",
        "theme": "creative_purple", "narrative": "inspire", "delivery": "showcase",
        "pages": [
            {"type": "cover", "title": "产品名 + 发布主张"},
            {"type": "quote", "title": "我们相信……"},
            {"type": "content", "title": "用户共鸣故事"},
            {"type": "section", "title": "全新能力"},
            {"type": "content", "title": "核心亮点", "items": ["亮点一", "亮点二", "亮点三"]},
            {"type": "media", "title": "实景演示"},
            {"type": "summary", "title": "邀请体验"},
        ],
    },
    "xhs_knowledge": {
        "label": "小红书知识卡 (XHS Knowledge)",
        "description": "种草/知识科普：痛点→方法→清单（视觉吸睛）",
        "theme": "sunset_orange", "narrative": "inform", "delivery": "showcase",
        "pages": [
            {"type": "cover", "title": "标题党金句 + 封面"},
            {"type": "content", "title": "你是不是也……（痛点）"},
            {"type": "content", "title": "3 个方法", "items": ["方法一", "方法二", "方法三"]},
            {"type": "two_column", "title": "避坑清单", "items": ["别做", "要做"]},
            {"type": "summary", "title": "收藏 + 关注引导"},
        ],
    },
    "gov_report": {
        "label": "党政汇报 (Official Report)",
        "description": "国企/党政汇报：背景→成效→经验→计划（正式庄重）",
        "theme": "gov_red", "narrative": "inform", "delivery": "editable",
        "pages": [
            {"type": "cover", "title": "汇报主题"},
            {"type": "section", "title": "一、工作背景"},
            {"type": "content", "title": "主要成效", "items": ["成效一", "成效二"]},
            {"type": "chart", "title": "数据支撑"},
            {"type": "content", "title": "经验做法", "items": ["做法一", "做法二"]},
            {"type": "summary", "title": "下一步计划"},
        ],
    },
    "medical_science": {
        "label": "医疗科普 (Medical Science)",
        "description": "健康/医学科普：概念→原理→建议",
        "theme": "medical_blue", "narrative": "teach", "delivery": "editable",
        "pages": [
            {"type": "cover", "title": "科普主题"},
            {"type": "section", "title": "学习目标"},
            {"type": "content", "title": "核心概念", "items": ["概念一", "概念二"]},
            {"type": "content", "title": "发生原理", "items": ["机制一", "机制二"]},
            {"type": "media", "title": "图示 / 案例"},
            {"type": "summary", "title": "健康建议"},
        ],
    },
    "ecom_promo": {
        "label": "电商大促 (E-com Promo)",
        "description": "直播/大促主视觉：利益点→爆款→倒计时（转化导向）",
        "theme": "ecommerce_orange", "narrative": "inspire", "delivery": "showcase",
        "pages": [
            {"type": "cover", "title": "大促主视觉 + 利益点"},
            {"type": "content", "title": "为什么买", "items": ["痛点", "爽点"]},
            {"type": "media", "title": "爆款展示"},
            {"type": "chart", "title": "价格对比 / 折扣力度"},
            {"type": "summary", "title": "立即抢购（倒计时）"},
        ],
    },
    "guochao_brand": {
        "label": "国潮品牌 (Guochao Brand)",
        "description": "国风品牌故事：文化→匠心→主张（视觉天花板）",
        "theme": "guochao_red", "narrative": "inspire", "delivery": "showcase",
        "pages": [
            {"type": "cover", "title": "品牌名 + 文化主张"},
            {"type": "quote", "title": "东方美学 · 当代表达"},
            {"type": "content", "title": "文化溯源", "items": ["元素一", "元素二"]},
            {"type": "media", "title": "匠心工艺"},
            {"type": "summary", "title": "邀请共赏"},
        ],
    },
    "fintech_report": {
        "label": "金融研报 (Fintech Report)",
        "description": "行业/数据研报：摘要→数据→结论",
        "theme": "fintech_green", "narrative": "inform", "delivery": "editable",
        "pages": [
            {"type": "cover", "title": "研报标题"},
            {"type": "section", "title": "摘要"},
            {"type": "chart", "title": "核心数据"},
            {"type": "content", "title": "趋势判断", "items": ["判断一", "判断二"]},
            {"type": "two_column", "title": "风险与机会", "items": ["风险", "机会"]},
            {"type": "summary", "title": "投资建议"},
        ],
    },
}

DEFAULT_TEMPLATE = "startup_pitch"
TEMPLATE_KEYS = ["label", "description", "theme", "narrative", "delivery", "pages"]


def _themes_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "themes"


def load_templates(templates_dir: Path | None = None,
                   builtin: dict | None = None) -> dict:
    """Return {id: template}. Disk templates/*.json override builtins."""
    builtin = builtin if builtin is not None else BUILTIN_TEMPLATES
    out: dict = dict(builtin)
    d = templates_dir or (Path(__file__).resolve().parent.parent / "templates")
    if d.is_dir():
        for p in sorted(d.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if all(k in data for k in TEMPLATE_KEYS):
                out[p.stem] = data
    return out


def select_template(brief: dict, templates: dict) -> dict:
    tid = brief.get("template") or DEFAULT_TEMPLATE
    return templates.get(tid, templates.get(DEFAULT_TEMPLATE, {}))


def _validate_one(tid: str, t: dict, themes: set) -> list[str]:
    errs = []
    for k in TEMPLATE_KEYS:
        if k not in t:
            errs.append(f"[{tid}] missing key: {k}")
    if t.get("theme") and themes and t["theme"] not in themes:
        errs.append(f"[{tid}] unknown theme: {t['theme']}")
    if t.get("narrative") not in ("persuade", "inform", "teach", "inspire"):
        errs.append(f"[{tid}] bad narrative: {t.get('narrative')}")
    if t.get("delivery") not in ("editable", "showcase"):
        errs.append(f"[{tid}] bad delivery: {t.get('delivery')}")
    if not isinstance(t.get("pages"), list) or not t["pages"]:
        errs.append(f"[{tid}] pages must be a non-empty list")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description="PPT Pro Studio template market")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="print template catalog")
    p_show = sub.add_parser("show", help="print one template")
    p_show.add_argument("id")
    p_val = sub.add_parser("validate", help="validate a brief's template / all templates")
    p_val.add_argument("path", nargs="?", default=None)
    p_init = sub.add_parser("init", help="materialize templates/*.json")
    p_init.add_argument("--dir", default=None)
    p_app = sub.add_parser("apply", help="scaffold a brief.json from a template")
    p_app.add_argument("id")
    p_app.add_argument("--out", required=True)

    args = ap.parse_args()
    TMPL_DIR = Path(args.dir).resolve() if getattr(args, "dir", None) \
        else Path(__file__).resolve().parent.parent / "templates"

    if args.cmd == "list":
        print(f"{len(BUILTIN_TEMPLATES)} templates:")
        for tid, t in BUILTIN_TEMPLATES.items():
            print(f"  {tid:16s} {t['label']:28s} [{t['narrative']}/{t['delivery']}] {t['theme']}")
        return 0

    if args.cmd == "show":
        t = BUILTIN_TEMPLATES.get(args.id)
        if not t:
            print(f"unknown template: {args.id}", file=sys.stderr); return 2
        print(json.dumps(t, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "validate":
        themes = set()
        tp = _themes_dir()
        if tp.is_dir():
            themes = {p.stem for p in tp.glob("*.json")}
        # validate the whole builtin catalog
        all_errs = []
        for tid, t in BUILTIN_TEMPLATES.items():
            all_errs += _validate_one(tid, t, themes)
        if args.path:
            brief = json.loads(Path(args.path).read_text(encoding="utf-8"))
            t = select_template(brief, BUILTIN_TEMPLATES)
            if not t:
                print(f"brief references unknown template: {brief.get('template')}")
                return 2
            print(f"ok: template '{brief.get('template')}' -> {t['label']}")
            return 0
        if all_errs:
            print("\n".join(all_errs)); return 1
        print(f"ok: {len(BUILTIN_TEMPLATES)} templates valid")
        return 0

    if args.cmd == "init":
        TMPL_DIR.mkdir(parents=True, exist_ok=True)
        for tid, t in BUILTIN_TEMPLATES.items():
            (TMPL_DIR / f"{tid}.json").write_text(
                json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"template market materialized: {len(BUILTIN_TEMPLATES)} templates -> {TMPL_DIR}")
        return 0

    if args.cmd == "apply":
        t = BUILTIN_TEMPLATES.get(args.id)
        if not t:
            print(f"unknown template: {args.id}", file=sys.stderr); return 2
        brief = {
            "template": args.id,
            "topic": t["label"],
            "audience": "",
            "goal": t["narrative"],
            "narrative": t["narrative"],
            "delivery": t["delivery"],
            "theme": t["theme"],
            "length": len(t["pages"]),
            "sections": max(3, min(6, len(t["pages"]) // 2)),
            "constraints": "",
            "acceptance": "可编辑/无水印/中文正常" if t["delivery"] == "editable"
                          else "视觉震撼、适合演示/路演",
            "pages": t["pages"],
        }
        Path(args.out).write_text(json.dumps(brief, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        print(f"brief scaffold -> {args.out} ({len(t['pages'])} pages, "
              f"theme={t['theme']}, delivery={t['delivery']})")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
