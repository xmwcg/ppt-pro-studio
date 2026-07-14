#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_market.py — PPT Pro Studio theme market (主题市场).

A theme is a complete, editable design token set:
    { label, bg, surface, primary, secondary, text, muted, accent, line, font }

This module is the single source of truth for the bundled catalog and the
loader both render engines import. Themes live as standalone JSON files under
`themes/` so users can add their own without touching engine code — that is the
"market": browse, pick, and extend.

CLI:
    python3 theme_market.py list                 # print the catalog
    python3 theme_market.py show <name>          # print one theme's tokens
    python3 theme_market.py validate <brief.json>  # does the brief's theme exist?
    python3 theme_market.py init [--dir themes]  # (re)materialize themes/*.json

Programmatic:
    from theme_market import load_themes, select_theme
    THEMES = load_themes(themes_dir)             # themes/*.json merged w/ builtin
    pal = select_theme(brief, THEMES)            # brief['theme']|brief['style']
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical bundled catalog. These are ALSO written out as themes/*.json by
# `init` so the on-disk market mirrors this source of truth.
# Every theme carries a 9-token palette + a human label + a CJK-friendly font.
# ---------------------------------------------------------------------------
BUILTIN_THEMES = {
    "tech_dark": {
        "label": "深色科技风 (Tech Dark)", "mode": "dark",
        "bg": "0D1117", "surface": "151D2E", "primary": "D4A060",
        "secondary": "58A6FF", "text": "FFFFFF", "muted": "8B949E",
        "accent": "3FB950", "line": "30363D", "font": "Microsoft YaHei",
    },
    "business_blue": {
        "label": "商务蓝 (Business Blue)", "mode": "light",
        "bg": "FFFFFF", "surface": "F2F6FC", "primary": "1F4E79",
        "secondary": "2E75B6", "text": "1A1A1A", "muted": "5A5A5A",
        "accent": "C55A11", "line": "D6E0F0", "font": "Microsoft YaHei",
    },
    "creative_purple": {
        "label": "创意紫 (Creative Purple)", "mode": "dark",
        "bg": "1B1033", "surface": "2A1B4A", "primary": "C77DFF",
        "secondary": "7B2FBE", "text": "F5EEFF", "muted": "B39DCE",
        "accent": "FF8FB1", "line": "3D2A63", "font": "Microsoft YaHei",
    },
    "academic_white": {
        "label": "学术白 (Academic White)", "mode": "light",
        "bg": "FFFFFF", "surface": "FAFAFA", "primary": "202020",
        "secondary": "006633", "text": "1A1A1A", "muted": "666666",
        "accent": "B00020", "line": "DDDDDD", "font": "Microsoft YaHei",
    },
    "minimal_gray": {
        "label": "简约灰 (Minimal Gray)", "mode": "light",
        "bg": "FAFAFA", "surface": "F0F0F0", "primary": "222222",
        "secondary": "666666", "text": "1A1A1A", "muted": "999999",
        "accent": "007ACC", "line": "E0E0E0", "font": "Microsoft YaHei",
    },
    "fintech_green": {
        "label": "金融绿 (Fintech Green)", "mode": "dark",
        "bg": "0B1F17", "surface": "122B20", "primary": "2EA66B",
        "secondary": "4FD1A1", "text": "EAF6F0", "muted": "7FA593",
        "accent": "F2B705", "line": "1E3A2C", "font": "Microsoft YaHei",
    },
    "sunset_orange": {
        "label": "暖阳橙 (Sunset Orange)", "mode": "dark",
        "bg": "1A1206", "surface": "2A1D0C", "primary": "E8843C",
        "secondary": "F2B705", "text": "FFF3E6", "muted": "B58A5E",
        "accent": "5BC0EB", "line": "3A2A14", "font": "Microsoft YaHei",
    },
    "mono_ink": {
        "label": "极简墨 (Mono Ink)", "mode": "dark",
        "bg": "0A0A0A", "surface": "161616", "primary": "FFFFFF",
        "secondary": "A0A0A0", "text": "FFFFFF", "muted": "7A7A7A",
        "accent": "FF4D4D", "line": "2A2A2A", "font": "Microsoft YaHei",
    },
    "guochao_red": {
        "label": "国潮红 (Guochao Red)", "mode": "dark",
        "bg": "1A0808", "surface": "2A1010", "primary": "C8102E",
        "secondary": "2A9D8F", "text": "FBF3E8", "muted": "B8897A",
        "accent": "E8B04B", "line": "3D1A1A", "font": "Microsoft YaHei",
    },
    "medical_blue": {
        "label": "医疗蓝 (Medical Blue)", "mode": "light",
        "bg": "F4F9FC", "surface": "E3F0F8", "primary": "0B6E9E",
        "secondary": "16A2C7", "text": "1A2B36", "muted": "5B7C8D",
        "accent": "2EA66B", "line": "C9E2F0", "font": "Microsoft YaHei",
    },
    "ecommerce_orange": {
        "label": "电商橙 (E-commerce Orange)", "mode": "light",
        "bg": "FFF7F0", "surface": "FFE9D6", "primary": "FF6A00",
        "secondary": "FF3D77", "text": "2B1A12", "muted": "9A7B68",
        "accent": "FFC400", "line": "FFD9BE", "font": "Microsoft YaHei",
    },
    "gov_red": {
        "label": "党政红 (Official Red)", "mode": "light",
        "bg": "FFFFFF", "surface": "FBEAEC", "primary": "C8102E",
        "secondary": "9E1B32", "text": "1A1A1A", "muted": "6B6B6B",
        "accent": "D4AF37", "line": "E6C9CE", "font": "Microsoft YaHei",
    },
}

DEFAULT_THEME = "tech_dark"
# Required token keys for a valid theme file.
THEME_KEYS = ["label", "mode", "bg", "surface", "primary", "secondary",
              "text", "muted", "accent", "line", "font"]

# ANSI swatch helper for the `list` view.
def _swatch(hex_str: str) -> str:
    r = int(hex_str[0:2], 16); g = int(hex_str[2:4], 16); b = int(hex_str[4:6], 16)
    return f"\033[48;2;{r};{g};{b}m   \033[0m"


# ---------------------------------------------------------------------------
# WCAG contrast utilities (P3-12). A theme is only as good as its readability.
# ---------------------------------------------------------------------------
def _rel_luminance(hex_str: str) -> float:
    """Relative luminance per WCAG 2.1 (0..1)."""
    r, g, b = (int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    def _lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast_ratio(hex1: str, hex2: str) -> float:
    """WCAG contrast ratio between two hex colors (no '#'). >=4.5 = AA, >=7 = AAA."""
    l1 = _rel_luminance(hex1)
    l2 = _rel_luminance(hex2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def contrast_grade(ratio: float) -> str:
    """Human-readable WCAG grade."""
    if ratio >= 7.0:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if ratio >= 3.0:
        return "AA Large"
    return "FAIL"


def check_contrast(theme: dict) -> dict:
    """Check key color pairs in a theme for WCAG compliance.

    Returns {pair: (ratio, grade)} for text/bg, primary/bg, accent/bg,
    muted/bg. Any FAIL means the theme needs adjustment.
    """
    pairs = {
        "text/bg": ("text", "bg"),
        "primary/bg": ("primary", "bg"),
        "accent/bg": ("accent", "bg"),
        "muted/bg": ("muted", "bg"),
    }
    result = {}
    for name, (fg, bg) in pairs.items():
        ratio = contrast_ratio(theme[fg], theme[bg])
        result[name] = (round(ratio, 1), contrast_grade(ratio))
    return result


def _themes_dir(default: str | None = None) -> Path:
    if default:
        return Path(default)
    here = Path(__file__).resolve().parent
    return here.parent / "themes"


def load_themes(themes_dir: str | Path | None = None,
                builtin: dict | None = None) -> dict:
    """Load the theme market. Merges on-disk themes/*.json OVER the builtin
    fallback so engines keep working even when the themes/ dir is absent or a
    single file is missing. Returns {name: tokens}."""
    merged = dict(builtin or {})
    td = _themes_dir(themes_dir)
    if td.exists():
        for f in sorted(td.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                name = f.stem
                if all(k in data for k in THEME_KEYS):
                    merged[name] = data
            except Exception:
                continue
    if not merged:
        merged = dict(BUILTIN_THEMES)
    return merged


def select_theme(brief: dict, themes: dict | None = None) -> dict:
    """Pick a palette from a brief. Accepts `theme` or `style` (alias). Falls
    back to DEFAULT_THEME when the key is unknown/missing."""
    themes = themes or load_themes()
    key = brief.get("theme") or brief.get("style")
    return themes.get(key, themes.get(DEFAULT_THEME, BUILTIN_THEMES[DEFAULT_THEME]))


def cmd_init(args):
    td = _themes_dir(args.dir)
    td.mkdir(parents=True, exist_ok=True)
    for name, toks in BUILTIN_THEMES.items():
        (td / f"{name}.json").write_text(
            json.dumps(toks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Catalog README describing the market + how to add a custom theme.
    catalog = "# 主题市场 / Theme Market\n\n"
    catalog += "Each file is a standalone, editable theme. Engines load every "
    catalog += "`*.json` here at render time; the brief picks one via `theme` "
    catalog += "(or `style`).\n\n"
    catalog += "## Bundled themes\n\n"
    catalog += "| key | label | primary | accent | bg |\n|---|---|---|---|---|\n"
    for name, t in BUILTIN_THEMES.items():
        catalog += (f"| `{name}` | {t['label']} | #{t['primary']} | "
                    f"#{t['accent']} | #{t['bg']} |\n")
    catalog += "\n## Add your own\n\n"
    catalog += "1. Copy any `*.json` to `my_theme.json`.\n"
    catalog += "2. Edit the 9 tokens (`bg, surface, primary, secondary, "
    catalog += "text, muted, accent, line, font`).\n"
    catalog += "3. Reference it: `{\"theme\": \"my_theme\", ...}` in your brief.\n"
    catalog += "4. Validate: `python3 theme_market.py validate my_brief.json`\n\n"
    catalog += "Tokens are OOXML-safe hex (no `#`). `font` should be a "
    catalog += "CJK-friendly face (default `Microsoft YaHei`).\n"
    (td / "README.md").write_text(catalog, encoding="utf-8")
    print(f"theme market materialized: {len(BUILTIN_THEMES)} themes -> {td}")
    return 0


def cmd_list(args):
    themes = load_themes(args.dir)
    print(f"\nPPT Pro Studio — Theme Market ({len(themes)} themes)\n")
    print(f"{'key':<16}{'label':<28}{'mode':<6}{'text/bg':>8}  primary  accent  bg")
    print("-" * 80)
    for name, t in themes.items():
        ratio = contrast_ratio(t["text"], t["bg"])
        grade = contrast_grade(ratio)
        mode = t.get("mode", "dark")
        print(f"{name:<16}{t['label']:<28}{mode:<6}"
              f"{ratio:>5.1f} {grade:<3}"
              f"  {_swatch(t['primary'])} #{t['primary']:<5}"
              f"  {_swatch(t['accent'])} #{t['accent']:<5}"
              f"  {_swatch(t['bg'])} #{t['bg']}")
    print()
    return 0


def cmd_show(args):
    themes = load_themes(args.dir)
    t = themes.get(args.name)
    if not t:
        sys.stderr.write(f"theme not found: {args.name}\n")
        return 1
    print(f"\ntheme: {args.name}  —  {t['label']}  [{t.get('mode','dark')}]\n")
    for k in THEME_KEYS:
        if k in ("label", "mode"):
            continue
        if k == "font":
            print(f"  {'font':<10} {t['font']}")
            continue
        print(f"  {k:<10} {_swatch(t[k])} #{t[k]}")
    # contrast report
    print(f"\n  WCAG Contrast Report:")
    for pair, (ratio, grade) in check_contrast(t).items():
        flag = "" if grade != "FAIL" else "  <-- BELOW WCAG MINIMUM"
        print(f"    {pair:<14} {ratio:>5.1f}:1  {grade}{flag}")
    print()
    return 0


def cmd_validate(args):
    brief_path = Path(args.brief)
    if not brief_path.exists():
        sys.stderr.write(f"brief not found: {brief_path}\n")
        return 2
    try:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except Exception as e:
        sys.stderr.write(f"invalid JSON: {e}\n")
        return 2
    themes = load_themes(args.dir)
    key = brief.get("theme") or brief.get("style") or DEFAULT_THEME
    if key in themes:
        print(f"ok: theme '{key}' -> {themes[key]['label']}")
        return 0
    sys.stderr.write(
        f"theme '{key}' not in market. Available: {', '.join(sorted(themes))}\n")
    return 1


def main():
    ap = argparse.ArgumentParser(description="PPT Pro Studio theme market")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list the theme catalog")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="show one theme's tokens")
    p.add_argument("name")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("validate", help="validate a brief's theme exists")
    p.add_argument("brief")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("init", help="(re)write themes/*.json from catalog")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_init)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
