#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — PPT Pro Studio unified entry (delivery router, P3-8/P3-2).

Reads a brief and routes to the right renderer by `brief['delivery']`:
  * 'showcase' -> Marp HTML path (ppt_marp.py)  -> visual-ceiling HTML (+PPTX/PDF)
  * 'editable' (default) -> core engines
        ppt_master_hifi.py (primary, native editable .pptx)
        ppt_studio_generate.py (fallback, python-pptx)

Usage:
    python3 scripts/generate.py brief.json --out output/deck.html
    python3 scripts/generate.py brief.json --out output/deck.pptx
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _run(script: str, brief: str, out: str) -> int:
    return subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script), brief, "--out", out],
        text=True).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="PPT Pro Studio unified generator")
    ap.add_argument("brief", help="brief.json path")
    ap.add_argument("--out", required=True, help="output path (.html/.pptx/.pdf)")
    ap.add_argument("--pdf", action="store_true", help="Marp: also PDF")
    ap.add_argument("--pptx", action="store_true", help="Marp: also PPTX")
    args = ap.parse_args()

    brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
    delivery = brief.get("delivery", "editable")

    if delivery == "showcase":
        cmd = [sys.executable, str(SCRIPT_DIR / "ppt_marp.py"), args.brief,
               "--out", args.out]
        if args.pdf:
            cmd.append("--pdf")
        if args.pptx:
            cmd.append("--pptx")
        return subprocess.run(cmd, text=True).returncode

    # editable: prefer hifi, fall back to python-pptx
    rc = _run("ppt_master_hifi.py", args.brief, args.out)
    if rc == 0:
        return 0
    sys.stderr.write("[generate] hifi failed, falling back to python-pptx\n")
    return _run("ppt_studio_generate.py", args.brief, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
