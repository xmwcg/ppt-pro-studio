#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the demo images used by the P2 图文混排 sample slide.

Reproducible asset builder so the sample deck is not tied to any external
image host. Output: examples/assets/dashboard.png, team.png (1200x900, 4:3).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

W, H = 1200, 900


def _vgrad(draw, w, h, top, bottom):
    for y in range(h):
        t = y / h
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _round_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def dashboard(path: Path):
    img = Image.new("RGB", (W, H), (13, 17, 23))
    d = ImageDraw.Draw(img)
    _vgrad(d, W, H, (13, 17, 23), (21, 29, 46))
    # header card
    _round_rect(d, (60, 60, 1140, 150), 18, (21, 29, 46))
    d.rounded_rectangle((90, 95, 130, 115), radius=8, fill=(63, 185, 80))
    d.text((150, 92), "Reasonix AI — 运营看板", fill=(212, 160, 96))
    d.text((150, 120), "实时 Agent 调用 / 收入 / 留存", fill=(139, 148, 158))
    # KPI cards
    kpis = [("今日调用", "1.24M", (63, 185, 80)),
            ("月活", "86.5K", (88, 166, 255)),
            ("MRR", "¥412K", (212, 160, 96))]
    cw = 340
    for i, (lab, val, col) in enumerate(kpis):
        x = 60 + i * (cw + 20)
        _round_rect(d, (x, 200, x + cw, 330), 16, (27, 36, 54))
        d.text((x + 28, 230), lab, fill=(139, 148, 158))
        d.text((x + 28, 265), val, fill=col)
    # mini bar chart
    _round_rect(d, (60, 370, 1140, 820), 16, (27, 36, 54))
    bars = [120, 210, 180, 320, 280, 410, 360, 470]
    bx = 110
    bw = 90
    base = 780
    for i, v in enumerate(bars):
        x = bx + i * (bw + 25)
        col = (212, 160, 96) if i % 2 == 0 else (88, 166, 255)
        d.rectangle((x, base - v, x + bw, base), fill=col)
    d.line([(90, base), (1110, base)], fill=(48, 54, 61), width=2)
    img.save(path, "PNG")


def team(path: Path):
    img = Image.new("RGB", (W, H), (11, 31, 23))
    d = ImageDraw.Draw(img)
    _vgrad(d, W, H, (11, 31, 23), (18, 43, 32))
    # network of nodes + links
    import math, random
    random.seed(7)
    nodes = []
    for _ in range(14):
        nodes.append((random.randint(120, 1080), random.randint(120, 780)))
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if j > i and math.dist(a, b) < 260:
                d.line([a, b], fill=(46, 166, 107, 120), width=2)
    for (x, y) in nodes:
        r = random.randint(14, 30)
        col = (79, 209, 161) if r > 22 else (242, 183, 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    d.text((60, 60), "协作网络", fill=(234, 246, 240))
    d.text((60, 95), "知识中枢连接每一个团队", fill=(127, 165, 147))
    img.save(path, "PNG")


def main():
    out = Path(__file__).resolve().parent
    dashboard(out / "dashboard.png")
    team(out / "team.png")
    print(f"assets written: {out / 'dashboard.png'}, {out / 'team.png'}")


if __name__ == "__main__":
    main()
