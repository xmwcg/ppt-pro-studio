#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_transitions.py — inject random per-slide page transitions (翻页随机动画).

Uses ppt-master's vetted OOXML transition core (pptx_transitions) so the
result is a real PowerPoint/Keynote-native page transition, not a hack.
Works on ANY .pptx (ppt-master SVG->PPTX output or python-pptx output).

No network, no watermarks. MIT-0.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

# Locate the bundled ppt-master transition core (vendored for offline use).
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    _HERE / "vendor" / "ppt-master-scripts",
    _HERE.parent / "vendor" / "ppt-master-scripts",
]
for _c in _CANDIDATES:
    if (_c / "pptx_transitions.py").exists():
        sys.path.insert(0, str(_c))
        break

from pptx import Presentation
from pptx_transitions import (  # noqa: E402
    EnterUpdate,
    AdvanceUpdate,
    apply_slide_motion,
    TRANSITIONS,
)


def add_random_transitions(pptx_path, seed=None, duration=0.5):
    """Apply a random transition effect to every slide. Returns effect list."""
    prs = Presentation(pptx_path)
    rnd = random.Random(seed)
    effects = list(TRANSITIONS.keys())
    applied = []
    for slide in prs.slides:
        eff = rnd.choice(effects)
        apply_slide_motion(
            slide._element,
            enter=EnterUpdate(policy="replace", effect=eff, duration=duration),
            advance=AdvanceUpdate(mode="click"),
        )
        applied.append(eff)
    prs.save(pptx_path)
    return applied


def main():
    ap = argparse.ArgumentParser(description="Add random slide transitions")
    ap.add_argument("pptx", help="path to .pptx")
    ap.add_argument("--seed", type=int, default=None,
                    help="random seed (stable repeats); omit for full random")
    ap.add_argument("--duration", type=float, default=0.5,
                    help="transition duration in seconds")
    args = ap.parse_args()
    applied = add_random_transitions(args.pptx, seed=args.seed,
                                     duration=args.duration)
    print("ok transitions applied=%d distinct=%d effects=%s" % (
        len(applied), len(set(applied)), sorted(set(applied))))


if __name__ == "__main__":
    main()
