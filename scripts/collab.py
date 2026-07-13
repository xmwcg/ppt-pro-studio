#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collab.py — PPT Pro Studio collaboration helper (P3-11).

Three commands:
  1. serve  — start a LAN HTTP server for HTML deck preview (auto-detects IP).
  2. export — export brief.json to Markdown for Lexiang / Tencent Docs import.
  3. init   — scaffold a git-versioned project structure (briefs/ + output/).

Usage:
    python3 scripts/collab.py serve  --dir output --port 8848
    python3 scripts/collab.py export --brief brief.json --out deck.md
    python3 scripts/collab.py init   [--dir ./my-deck-project]
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import socket
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# serve — LAN HTTP server
# ---------------------------------------------------------------------------
def cmd_serve(args) -> int:
    d = Path(args.dir).resolve()
    if not d.is_dir():
        print(f"directory not found: {d}", file=sys.stderr)
        return 2

    port = args.port
    os.chdir(str(d))

    # detect LAN IP
    lan_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("0.0.0.0", port), handler)

    # list HTML files
    htmls = sorted(d.glob("*.html"))
    print(f"\n  PPT Pro Studio — LAN Preview Server")
    print(f"  {'=' * 50}")
    print(f"  Serving:  {d}")
    print(f"  Local:    http://localhost:{port}")
    print(f"  LAN:      http://{lan_ip}:{port}")
    if htmls:
        print(f"  {'─' * 50}")
        print(f"  Available decks:")
        for h in htmls:
            print(f"    -> http://{lan_ip}:{port}/{h.name}")
    print(f"  {'─' * 50}")
    print(f"  Press Ctrl+C to stop.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        httpd.server_close()
    return 0


# ---------------------------------------------------------------------------
# export — brief.json -> Markdown for Lexiang / Tencent Docs
# ---------------------------------------------------------------------------
def cmd_export(args) -> int:
    brief_path = Path(args.brief)
    if not brief_path.exists():
        print(f"brief not found: {brief_path}", file=sys.stderr)
        return 2

    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    lines: list[str] = []

    # title
    topic = brief.get("topic", "Untitled Deck")
    lines.append(f"# {topic}\n")

    # meta
    meta_parts = []
    for k in ("audience", "goal", "narrative", "delivery", "theme"):
        v = brief.get(k)
        if v:
            meta_parts.append(f"**{k}**: {v}")
    if meta_parts:
        lines.append("> " + " | ".join(meta_parts) + "\n")

    lines.append(f"> {brief.get('length', '?')} pages | "
                 f"template: {brief.get('template', 'none')}\n")

    # pages
    pages = brief.get("pages", [])
    for i, pg in enumerate(pages, 1):
        pg_type = pg.get("type", "content")
        title = pg.get("title", f"Page {i}")
        lines.append(f"## {i}. [{pg_type}] {title}\n")

        # items
        items = pg.get("items", [])
        if items:
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

        # columns
        cols = pg.get("columns", [])
        if cols:
            for col in cols:
                lines.append(f"### {col.get('title', '')}")
                for item in col.get("items", []):
                    lines.append(f"- {item}")
                lines.append("")

        # table
        rows = pg.get("rows", [])
        headers = pg.get("headers", [])
        if headers:
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in rows:
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
            lines.append("")

        # chart
        if pg_type == "chart":
            series = pg.get("series", [])
            if series:
                lines.append("**Data:**")
                for s in series:
                    lines.append(f"- {s.get('label', '')}: {s.get('value', '')}")
                lines.append("")

        # notes
        notes = pg.get("notes", "")
        if notes:
            lines.append(f"> **Speaker notes:** {notes}\n")

    # acceptance
    acc = brief.get("acceptance", "")
    if acc:
        lines.append(f"---\n**Acceptance criteria:** {acc}\n")

    # constraints
    cons = brief.get("constraints", "")
    if cons:
        lines.append(f"**Constraints:** {cons}\n")

    out_path = Path(args.out)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"exported {len(pages)} pages -> {out_path}")
    print(f"paste into Lexiang / Tencent Docs / Notion / Feishu for collaboration.")
    return 0


# ---------------------------------------------------------------------------
# init — scaffold a git-versioned project
# ---------------------------------------------------------------------------
def cmd_init(args) -> int:
    d = Path(args.dir).resolve()
    if d.exists() and any(d.iterdir()):
        print(f"directory not empty: {d}", file=sys.stderr)
        return 2

    (d / "briefs").mkdir(parents=True, exist_ok=True)
    (d / "output").mkdir(parents=True, exist_ok=True)

    # .gitattributes
    (d / ".gitattributes").write_text(
        "*.pptx binary\n*.pdf  binary\n*.html diff=html\n*.json diff=json\n",
        encoding="utf-8")

    # .gitignore
    (d / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n.DS_Store\nThumbs.db\n",
        encoding="utf-8")

    # README
    (d / "README.md").write_text(
        f"# {d.name}\n\n"
        "PPT Pro Studio project — briefs and outputs are git-versioned.\n\n"
        "## Structure\n"
        "- `briefs/`  — versioned brief JSON files\n"
        "- `output/`  — rendered .pptx / .html / .pdf\n\n"
        "## Workflow\n"
        "1. Edit `briefs/v1.json` (use `ui/console.html` or `prompt_enhance.py`)\n"
        "2. Render: `python3 scripts/generate.py briefs/v1.json --out output/v1.pptx`\n"
        "3. QA:     `python3 scripts/qa2.py output/v1.pptx`\n"
        "4. Commit: `git add briefs/v1.json output/v1.pptx && git commit -m 'v1'`\n"
        "5. Preview (HTML): `python3 scripts/collab.py serve --dir output --port 8848`\n"
        "6. Collaborate:    `python3 scripts/collab.py export --brief briefs/v1.json --out v1.md`\n"
        "   -> paste v1.md into Lexiang / Tencent Docs for team review\n",
        encoding="utf-8")

    print(f"project scaffolded: {d}")
    print(f"  briefs/  — put your brief JSON here")
    print(f"  output/  — rendered artifacts go here")
    print(f"  .gitattributes + .gitignore + README.md ready")
    print(f"\n  cd {d} && git init && git add -A && git commit -m 'init'")
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="PPT Pro Studio collaboration helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_serve = sub.add_parser("serve", help="start LAN HTTP server for HTML preview")
    p_serve.add_argument("--dir", default="output", help="directory to serve")
    p_serve.add_argument("--port", type=int, default=8848, help="port number")

    p_export = sub.add_parser("export", help="export brief to Markdown for collaboration")
    p_export.add_argument("--brief", required=True, help="brief.json path")
    p_export.add_argument("--out", required=True, help="output .md path")

    p_init = sub.add_parser("init", help="scaffold a git-versioned project")
    p_init.add_argument("--dir", default="./deck-project", help="project directory")

    args = ap.parse_args()
    if args.cmd == "serve":
        return cmd_serve(args)
    if args.cmd == "export":
        return cmd_export(args)
    if args.cmd == "init":
        return cmd_init(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
