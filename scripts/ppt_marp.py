#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ppt_marp.py — Marp HTML showcase path (P3-8: 演示天花板).

Renders a brief into a high-visual HTML deck using Marp. One source (the brief)
also yields optional PPTX/PDF for distribution. When the user wants an *editable*
.ppptx, use the core engines instead (ppt_master_hifi / ppt_studio_generate).
Routing is decided by `brief['delivery'] == 'showcase'`.

The slide theme CSS is generated from the brief's theme tokens (via theme_market)
so every bundled theme gets a matching showcase skin — no hand-written CSS drift.

Requires `@marp-team/marp-cli` (Node 18+). HTML always works; PPTX/PDF need a
Chromium browser and are produced only when one is detected.

Usage:
    python3 scripts/ppt_marp.py brief.json --out output/show.html [--pdf] [--pptx]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Allow `import theme_market` when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme_market import load_themes, select_theme  # noqa: E402

MANAGED_MARP = Path(
    r"C:/Users/Administrator/.workbuddy/binaries/node/workspace/node_modules/.bin/marp")


def _find_marp():
    """Return a command prefix (list) to launch marp-cli, or None.

    Prefers a Node-launched scoped package (works on Windows where the
    `.bin/marp` sh script cannot be executed directly). Falls back to a
    `marp` on PATH.
    """
    import json as _json
    node = shutil.which("node")
    spots = []
    if os.environ.get("MARPCLI_BIN"):
        spots.append(os.environ["MARPCLI_BIN"])
    spots.append(
        r"C:/Users/Administrator/.workbuddy/binaries/node/workspace/"
        r"node_modules/@marp-team/marp-cli")
    for sp in spots:
        p = Path(sp)
        if p.is_dir() and (p / "package.json").exists():
            try:
                pkg = _json.loads((p / "package.json").read_text(encoding="utf-8"))
            except Exception:
                pkg = {}
            binv = pkg.get("bin", {})
            bin_rel = binv.get("marp") if isinstance(binv, dict) else binv
            if bin_rel and node:
                entry = p / bin_rel
                if entry.exists():
                    return [node, str(entry)]
        elif p.is_file() and node:
            return [node, str(p)]
    m = shutil.which("marp")
    if m:
        return [m]
    return None


def _find_chrome() -> str | None:
    for b in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(b)
        if p:
            return p
    # common Windows paths
    for p in (r"C:/Program Files/Google/Chrome/Application/chrome.exe",
              r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"):
        if Path(p).exists():
            return p
    return None


def build_css(theme: dict) -> str:
    """Generate a showcase CSS skin from theme tokens."""
    def c(key):
        return "#" + theme.get(key, "000000")
    bg, surface, primary = c("bg"), c("surface"), c("primary")
    secondary, text, muted = c("secondary"), c("text"), c("muted")
    accent, line, font = c("accent"), c("line"), theme.get("font", "Microsoft YaHei")
    return f"""/* PPT Pro Studio showcase skin — generated from {theme.get('label')} */
section {{
  background: radial-gradient(circle at 18% 18%, {surface}, {bg});
  color: {text};
  font-family: "{font}", "PingFang SC", "Hiragino Sans GB", sans-serif;
  font-size: 30px;
  padding: 64px 88px;
  justify-content: center;
}}
h1 {{ color: {primary}; font-size: 68px; margin: 0 0 .25em; letter-spacing: 2px;
     text-shadow: 0 2px 24px rgba(0,0,0,.35); }}
h2 {{ color: {primary}; font-size: 46px; border-left: 8px solid {accent};
     padding-left: 20px; margin: 0 0 .4em; }}
h3 {{ color: {secondary}; font-size: 34px; }}
ul {{ margin: .2em 0; }}
li {{ margin: .3em 0; line-height: 1.5; }}
ul li::marker {{ color: {accent}; }}
strong, b {{ color: {accent}; }}
a {{ color: {secondary}; }}
blockquote {{
  border-left: 10px solid {accent}; padding: .4em 1em; color: {text};
  font-size: 42px; line-height: 1.4; background: {surface};
  border-radius: 14px; box-shadow: 0 8px 30px rgba(0,0,0,.25);
}}
.card {{ background: {surface}; border: 1px solid {line}; border-radius: 18px;
        padding: 26px 30px; box-shadow: 0 10px 30px rgba(0,0,0,.22); }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 44px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 24px; }}
th, td {{ border: 1px solid {line}; padding: 10px 16px; }}
th {{ background: {surface}; color: {primary}; }}
tr:nth-child(even) td {{ background: {surface}; }}
section::after {{
  content: "{theme.get('label','')}"; font-size: 16px; color: {muted};
}}
footer {{ color: {muted}; font-size: 16px; }}
img {{ border-radius: 14px; max-height: 60vh; box-shadow: 0 10px 30px rgba(0,0,0,.3); }}
"""


def render_page(p: dict) -> str:
    t = p.get("type", "content")
    title = p.get("title", "")
    items = p.get("items") or []
    notes = p.get("notes", "")
    L: list[str] = []
    if t == "cover":
        L.append(f"# {title}")
        if p.get("subtitle"):
            L.append(f"\n<p class='card' style='display:inline-block;font-size:32px;color:{ '#'+p.get('accent','accent') if False else 'inherit'}'>{p['subtitle']}</p>")
    elif t == "section":
        L.append(f"# {title}")
    elif t == "quote":
        L.append(f"> {title}")
        L += [f"> {it}" for it in items]
    elif t == "chart":
        L.append(f"## {title}")
        L.append("")
        L.append("> 📊 数据图表（可编辑版见 .pptx 生产件）")
        L += [f"- {it}" for it in items]
    elif t == "table":
        L.append(f"## {title}")
        rows = p.get("rows") or []
        if rows:
            L.append("")
            L.append("| " + " | ".join(rows[0]) + " |")
            L.append("| " + " | ".join(["---"] * len(rows[0])) + " |")
            for r in rows[1:]:
                L.append("| " + " | ".join(r) + " |")
    elif t == "timeline":
        L.append(f"## {title}")
        L += [f"1. {it}" for it in items]
    elif t == "media":
        L.append(f"## {title}")
        if p.get("image"):
            L.append(f"\n![{p.get('caption', '')}]({p['image']})")
        else:
            L += [f"- {it}" for it in items]
    elif t in ("two_column", "content", "summary", "contact"):
        L.append(f"## {title}")
        L += [f"- {it}" for it in items]
        if t == "summary":
            L.append("\n> ✅ 行动号召")
    else:
        L.append(f"## {title}")
        L += [f"- {it}" for it in items]
    body = "\n".join(L)
    if notes:
        body += f"\n\n<!-- {notes} -->"
    return body


def build_markdown(brief: dict, css_name: str) -> str:
    pages = brief.get("pages") or []
    md = "---\n"
    md += f"theme: ./{css_name}\n"
    md += f"title: \"{brief.get('topic', 'Deck')}\"\n"
    md += "paginate: true\n"
    md += "size: 16:9\n"
    md += "---\n\n"
    for p in pages:
        md += render_page(p) + "\n\n---\n\n"
    return md


def main() -> int:
    ap = argparse.ArgumentParser(description="PPT Pro Studio — Marp showcase path")
    ap.add_argument("brief", help="brief.json (delivery should be 'showcase')")
    ap.add_argument("--out", required=True, help="output HTML path")
    ap.add_argument("--pdf", action="store_true", help="also emit PDF (needs Chrome)")
    ap.add_argument("--pptx", action="store_true", help="also emit PPTX (needs Chrome)")
    args = ap.parse_args()

    brief_path = Path(args.brief)
    if not brief_path.exists():
        sys.stderr.write(f"brief not found: {args.brief}\n")
        return 2
    brief = json.loads(brief_path.read_text(encoding="utf-8"))

    marp = _find_marp()
    if not marp:
        sys.stderr.write(
            "marp-cli not found. Install: npm i -g @marp-team/marp-cli "
            "(or set MARPCLI_BIN). HTML showcase needs it.\n")
        return 3

    THEMES = load_themes(builtin=None)
    theme = select_theme(brief, THEMES)
    if not theme:
        sys.stderr.write(f"unknown theme: {brief.get('theme') or brief.get('style')}\n")
        return 2

    out_html = Path(args.out)
    build_dir = out_html.parent
    build_dir.mkdir(parents=True, exist_ok=True)
    css_name = "_showcase_skin.css"
    (build_dir / css_name).write_text(build_css(theme), encoding="utf-8")
    md_path = build_dir / "_showcase.md"
    md_path.write_text(build_markdown(brief, css_name), encoding="utf-8")

    cmd = marp + [str(md_path), "--html", "-o", str(out_html)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr or r.stdout)
        return r.returncode
    print(f"showcase HTML -> {out_html} ({len(brief.get('pages', []))} slides, "
          f"theme={theme.get('label')})")

    chrome = _find_chrome()
    for fmt in ("pdf", "pptx"):
        if getattr(args, fmt):
            if not chrome:
                sys.stderr.write(
                    f"[skip] --{fmt} needs a Chromium browser; none detected.\n")
                continue
            out_f = out_html.with_suffix(f".{fmt}")
            rc = subprocess.run(marp + [str(md_path), f"--{fmt}", "-o", str(out_f)],
                                 capture_output=True, text=True)
            if rc.returncode == 0:
                print(f"showcase {fmt.upper()} -> {out_f}")
            else:
                sys.stderr.write(rc.stderr or rc.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
