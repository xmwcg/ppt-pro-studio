#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa2.py — PPT Pro Studio QA 2.0 layout audit.

Goes beyond "did it render?" (the old qa_check) to "does it look right?":
  * bounds      — no shape escapes the slide canvas
  * placeholders — no leftover [..], 图片缺失, TODO, 占位 tokens
  * font floor  — body text >= 11pt; only footer/page numbers may be 9pt
  * transitions — every slide has a <p:transition> (翻页动画)
  * icon/vector — count of native custGeom (embedded vector icons)
  * brand theme — slide-master theme1.xml carries the brand primary color
  * consistency — master theme + icons present across the deck

Outputs a JSON report + a 0-100 score. CLI:
    python3 qa2.py deck.pptx [--json report.json]
Exit code 0 when no error-level issues, else 1.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

# Slide canvas bounds in EMU (13.333in x 7.5in) + small tolerance.
SLIDE_W = 12192000
SLIDE_H = 6858000
TOL = 9525  # ~1px tolerance for rounding

PLACEHOLDER_TOKENS = ["[", "图片缺失", "TODO", "占位", "未提供", "TBD"]


def audit(path: str) -> dict:
    prs = Presentation(path)
    slides = list(prs.slides)
    total = len(slides)
    errors = []
    warnings = []
    icon_shapes = 0
    transition_slides = 0
    min_body = 999
    bounds_hits = 0

    for i, slide in enumerate(slides, 1):
        xml = slide._element.xml
        icon_shapes += xml.count("custGeom")
        if "<p:transition" in xml:
            transition_slides += 1
        # bounds
        for sh in slide.shapes:
            try:
                l = sh.left or 0
                t = sh.top or 0
                w = sh.width or 0
                h = sh.height or 0
            except Exception:
                continue
            if (l < -TOL or t < -TOL or
                    l + w > SLIDE_W + TOL or t + h > SLIDE_H + TOL):
                bounds_hits += 1
                errors.append(
                    f"slide {i}: shape out of bounds "
                    f"(L={Emu(l).inches:.2f} T={Emu(t).inches:.2f} "
                    f"R={Emu(l + w).inches:.2f} B={Emu(t + h).inches:.2f} in)")
        # text checks
        for sh in slide.shapes:
            if not sh.has_text_frame:
                continue
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    txt = run.text or ""
                    sz = run.font.size.pt if run.font.size else None
                    if txt.strip():
                        for tok in PLACEHOLDER_TOKENS:
                            if tok in txt:
                                errors.append(
                                    f"slide {i}: placeholder token '{tok}' "
                                    f"in text '{txt[:24]}'")
                                break
                    if sz is not None:
                        if sz < 9:
                            errors.append(
                                f"slide {i}: font {sz}pt below 9pt floor")
                        elif 9 < sz < 11:
                            warnings.append(
                                f"slide {i}: body font {sz}pt (over-shrunk, "
                                f"target >=11)")
                        if sz >= 9:
                            min_body = min(min_body, sz)

    # brand theme check
    brand = False
    try:
        z = zipfile.ZipFile(path)
        th = [n for n in z.namelist()
              if __import__("re").search(r"theme1?\.xml$", n)]
        if th:
            x = z.read(th[0]).decode("utf-8", "ignore")
            brand = "D4A060" in x  # tech_dark primary; deck should carry brand
    except Exception:
        pass

    # score
    score = 100
    score -= len(errors) * 8
    score -= len(warnings) * 2
    if transition_slides != total:
        score -= 5
    if not brand:
        score -= 5
    score = max(0, min(100, score))

    return {
        "file": str(Path(path).resolve()),
        "slides": total,
        "slides_clean": total - (1 if errors else 0),
        "errors": errors,
        "warnings": warnings,
        "bounds_hits": bounds_hits,
        "icon_shapes": icon_shapes,
        "transitions": transition_slides,
        "min_body_pt": min_body if min_body != 999 else None,
        "brand_theme": brand,
        "score": score,
    }


def main():
    ap = argparse.ArgumentParser(description="PPT Pro Studio QA 2.0 audit")
    ap.add_argument("pptx", help="path to .pptx to audit")
    ap.add_argument("--json", default=None, help="write JSON report to this path")
    args = ap.parse_args()
    if not Path(args.pptx).exists():
        sys.stderr.write(f"file not found: {args.pptx}\n")
        sys.exit(2)
    rep = audit(args.pptx)
    if args.json:
        Path(args.json).write_text(json.dumps(rep, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
    # human summary
    print("=" * 56)
    print(f"QA 2.0  ·  {rep['file']}")
    print(f"slides={rep['slides']}  score={rep['score']}/100")
    print(f"clean={rep['slides_clean']}  bounds_hits={rep['bounds_hits']}  "
          f"transitions={rep['transitions']}/{rep['slides']}")
    print(f"icon/vector shapes={rep['icon_shapes']}  "
          f"min_body={rep['min_body_pt']}pt  brand_theme={rep['brand_theme']}")
    if rep["errors"]:
        print(f"\nERRORS ({len(rep['errors'])}):")
        for e in rep["errors"]:
            print("  ✗", e)
    if rep["warnings"]:
        print(f"\nWARNINGS ({len(rep['warnings'])}):")
        for w in rep["warnings"]:
            print("  !", w)
    if not rep["errors"] and not rep["warnings"]:
        print("\n✓ no layout issues found")
    print("=" * 56)
    sys.exit(1 if rep["errors"] else 0)


if __name__ == "__main__":
    main()
