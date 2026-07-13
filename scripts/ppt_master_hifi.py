#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ppt_master_hifi.py — PPT Pro Studio PRIMARY render path (ppt-master SVG -> PPTX).

This is the recommended engine for PPT Pro Studio. It takes the same
structured `brief.json` used by the deterministic fallback renderer
(`ppt_studio_generate.py`) and routes it through *ppt-master*'s SVG ->
native PPTX engine (hugohe3/ppt-master, 16.6k stars, MIT — the highest-starred
PPTX skill). Output is vector-authored, fully editable, and ships with random
per-slide page transitions (翻页随机动画) via ppt-master's transition core.

Pipeline:
    brief.json  ->  <project>/svg_output/page_NNN.svg  (vector authoring)
               ->  <project>/spec_lock.md               (design tokens)
               ->  ppt-master scripts/svg_to_pptx.py     (SVG -> native .pptx)
               ->  add_transitions.py                    (random page flips)

All text is wrapped and clamped inside the 1280x720 canvas so nothing
overflows the slide. No network, no watermarks. MIT-0.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from icons import icon_svg, DEFAULT_ICON

# ---------------------------------------------------------------------------
# Design system — must stay in sync with ppt_studio_generate.py
# ---------------------------------------------------------------------------
PALETTES = {
    "tech_dark": {"bg": "0D1117", "surface": "151D2E", "primary": "D4A060",
                  "secondary": "58A6FF", "text": "FFFFFF", "muted": "8B949E",
                  "accent": "3FB950", "line": "30363D", "font": "Microsoft YaHei"},
    "business_blue": {"bg": "FFFFFF", "surface": "F2F6FC", "primary": "1F4E79",
                      "secondary": "2E75B6", "text": "1A1A1A", "muted": "5A5A5A",
                      "accent": "C55A11", "line": "D6E0F0", "font": "Microsoft YaHei"},
    "creative_purple": {"bg": "1B1033", "surface": "2A1B4A", "primary": "C77DFF",
                        "secondary": "7B2FBE", "text": "F5EEFF", "muted": "B39DCE",
                        "accent": "FF8FB1", "line": "3D2A63", "font": "Microsoft YaHei"},
    "academic_white": {"bg": "FFFFFF", "surface": "FAFAFA", "primary": "202020",
                       "secondary": "006633", "text": "1A1A1A", "muted": "666666",
                       "accent": "B00020", "line": "DDDDDD", "font": "Microsoft YaHei"},
    "minimal_gray": {"bg": "FAFAFA", "surface": "F0F0F0", "primary": "222222",
                     "secondary": "666666", "text": "1A1A1A", "muted": "999999",
                     "accent": "007ACC", "line": "E0E0E0", "font": "Microsoft YaHei"},
}

FONT = "Microsoft YaHei"
W, H = 1280, 720          # ppt169 canvas (matches ppt-master default)
SCALE = 96.0              # px per inch
PT2PX = 96.0 / 72.0       # pt -> px


def X(i: float) -> float:
    return i * SCALE


def Y(i: float) -> float:
    return i * SCALE


def PX(pt: float) -> float:
    return pt * PT2PX


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def _char_w(ch: str, size: float) -> float:
    return size if ord(ch) > 0x2E80 else size * 0.55


def wrap(text: str, size: float, max_w: float) -> list[str]:
    """Crude but robust CJK-safe line wrap by character width estimate."""
    if not text:
        return [""]
    lines, cur, width = [], "", 0.0
    for ch in text:
        cw = _char_w(ch, size)
        if width + cw > max_w and cur:
            lines.append(cur)
            cur, width = ch, cw
        else:
            cur += ch
            width += cw
    if cur:
        lines.append(cur)
    return lines


def _text(x: float, y_top: float, s: str, size: float, fill: str,
          bold: bool = False, align: str = "left", italic: bool = False) -> str:
    anchor = {"left": "start", "center": "middle", "right": "end"}[align]
    baseline = y_top + size * 0.86
    fs = f'font-size="{size:.1f}"'
    fw = ' font-weight="700"' if bold else ""
    fs_style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{baseline:.1f}" text-anchor="{anchor}" '
            f'{fs} fill="#{fill}" font-family="{FONT}"{fw}{fs_style}>{esc(s)}</text>')


def text_block(x: float, y: float, content: str, size: float, fill: str,
               bold: bool = False, align: str = "left", max_w: float = 1180.0,
               line_h: float | None = None) -> tuple[str, float]:
    """Render a (possibly multi-line) text block. Returns (svg, next_y)."""
    line_h = line_h or size * 1.25
    parts = content.split("\n")
    out = []
    cy = y
    for para in parts:
        for line in wrap(para, size, max_w):
            out.append(_text(x, cy, line, size, fill, bold, align))
            cy += line_h
    return "\n".join(out), cy


def vtext(x: float, y: float, content: str, size: float, fill: str, max_w: float,
          max_h: float | None = None, align: str = "left", bold: bool = False,
          italic: bool = False) -> tuple[str, float]:
    """Wrap text and shrink font until it fits both width (max_w) and height
    (max_h). Readability floor is 11pt: below that the text is truncated with
    an ellipsis instead of shrinking into an unreadable size. Returns
    (svg, next_y)."""
    if max_h is None:
        max_h = H - y - 4
    else:
        max_h = min(max_h, H - y - 4)
    max_h = max(max_h, size * 1.25)
    s = float(size)
    while True:
        lh = s * 1.25
        nlines = 0
        for para in content.split("\n"):
            nlines += max(1, len(wrap(para, s, max_w)))
        if nlines * lh <= max_h or s <= 11:
            break
        s -= 1.0
    s = max(s, 11.0)
    # Truncate (with ellipsis) if even the floor overflows the box height.
    while len(content) > 1:
        nlines = 0
        for para in content.split("\n"):
            nlines += max(1, len(wrap(para, s, max_w)))
        if nlines * s * 1.25 <= max_h:
            break
        content = content[:-1]
    if content and content != content.rstrip():
        content = content.rstrip() + "\u2026"
    svg, ny = text_block(x, y, content, s, fill, bold=bold, align=align,
                         max_w=max_w, line_h=s * 1.25)
    return svg, ny


def rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 0.0,
         opacity: float | None = None, stroke: str | None = None,
         stroke_w: float = 1.0) -> str:
    attrs = f'x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{fill}"'
    if rx:
        attrs += f' rx="{rx:.1f}"'
    if opacity is not None:
        attrs += f' opacity="{opacity:.2f}"'
    if stroke:
        attrs += f' stroke="#{stroke}" stroke-width="{stroke_w:.1f}"'
    return f"<rect {attrs}/>"


def line(x1: float, y1: float, x2: float, y2: float, stroke: str,
         w: float = 1.0) -> str:
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#{stroke}" stroke-width="{w:.1f}"/>')


def circle(cx: float, cy: float, r: float, fill: str) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#{fill}"/>'


# ---------------------------------------------------------------------------
# Slide SVG builders — every text element is wrapped & clamped (no overflow)
# ---------------------------------------------------------------------------
class SvgSlide:
    def __init__(self, pal: dict):
        self.p = pal

    def _bg(self):
        return rect(0, 0, W, H, self.p["bg"])

    def _icon(self, name, x, y, size_px, color=None):
        return icon_svg(name, x, y, size_px, color or self.p["primary"],
                        stroke_px=size_px * 0.06)

    def _footer(self, idx: int, footer: str, page_numbers: bool):
        out = []
        if footer:
            out.append(_text(X(0.5), Y(7.05), footer, PX(9), self.p["muted"]))
        if page_numbers:
            out.append(_text(X(12.3), Y(7.05), str(idx), PX(9),
                             self.p["muted"], align="right"))
        return "\n".join(out)

    def _title_bar(self, title, subtitle=None, num=None, stype="content",
                   icon=None):
        out = []
        name = icon or DEFAULT_ICON.get(stype, "list")
        out.append(self._icon(name, X(0.6), Y(0.42), PX(28)))
        t, _ = vtext(X(1.2), Y(0.4), title, PX(28), self.p["primary"], bold=True,
                     max_w=X(10.0), max_h=Y(0.7))
        out.append(t)
        out.append(rect(X(1.2), Y(1.12), X(2.2), PX(3), self.p["primary"]))
        if subtitle:
            s, _ = vtext(X(1.2), Y(1.22), subtitle, PX(14), self.p["secondary"],
                         max_w=X(11.0), max_h=Y(0.5))
            out.append(s)
        if num:
            n, _ = vtext(X(11.0), Y(0.4), num, PX(22), self.p["muted"], bold=True,
                         align="right", max_w=X(1.7), max_h=Y(0.7))
            out.append(n)
        return "\n".join(out)

    def cover(self, d):
        out = [self._bg()]
        title = d.get("title", "")
        sub = d.get("subtitle", "")
        badge = d.get("badge", "")
        icon = d.get("icon", "rocket")
        variant = d.get("variant", "centered")
        if variant == "left":
            out.append(self._icon(icon, X(0.9), Y(2.4), PX(48)))
            t, _ = vtext(X(1.1), Y(3.5), title, PX(40), self.p["primary"],
                         bold=True, max_w=X(10.5), max_h=Y(1.7))
            out.append(t)
            if sub:
                s, _ = vtext(X(1.1), Y(5.3), sub, PX(20), self.p["secondary"],
                             max_w=X(10.5), max_h=Y(1.0))
                out.append(s)
        else:
            out.append(self._icon(icon, W / 2 - PX(24), Y(1.5), PX(48)))
            t, _ = vtext(W / 2, Y(2.6), title, PX(46), self.p["primary"],
                         bold=True, align="center", max_w=X(11.3), max_h=Y(2.0))
            out.append(t)
            if sub:
                s, _ = vtext(W / 2, Y(4.2), sub, PX(20), self.p["secondary"],
                             align="center", max_w=X(11.3), max_h=Y(1.0))
                out.append(s)
        if badge:
            b, _ = vtext(W / 2, Y(5.4), badge, PX(13), self.p["muted"],
                         align="center", max_w=X(11.3), max_h=Y(0.5))
            out.append(b)
        return out

    def section(self, d):
        title = d.get("title", "")
        num = d.get("index")
        title_text = title
        if not num:
            sp = title.split(" ", 1)
            if sp[0].isdigit():
                num = sp[0]
                title_text = sp[1] if len(sp) > 1 else title
        out = [self._bg(),
               rect(0, Y(2.7), W, Y(2.0), self.p["surface"]),
               rect(0, Y(2.7), PX(3), Y(2.0), self.p["primary"]),
               line(X(3.4), Y(2.9), X(3.4), Y(4.5), self.p["line"], 1),
               f'<circle cx="{X(11.9):.1f}" cy="{Y(3.7):.1f}" r="{PX(46):.1f}" '
               f'fill="none" stroke="#{self.p["primary"]}" stroke-width="2" '
               f'opacity="0.5"/>']
        if num:
            out.append(_text(X(2.0), Y(3.15), num, PX(96), self.p["accent"],
                             bold=True, align="center"))
        tx = X(3.7) if num else X(1.7)
        t, _ = vtext(tx, Y(2.95), title_text, PX(34), self.p["primary"],
                     bold=True, max_w=X(7.7), max_h=Y(1.2))
        out.append(t)
        if d.get("subtitle"):
            s, _ = vtext(tx, Y(4.25), d["subtitle"], PX(14), self.p["muted"],
                         max_w=X(7.7), max_h=Y(0.5))
            out.append(s)
        return out

    def agenda(self, d):
        out = [self._bg(), self._title_bar(d.get("title", "目录"),
                                           d.get("subtitle"), stype="agenda")]
        items = d.get("items", [])
        n = len(items)
        top, bottom = Y(1.7), Y(6.9)
        gap = min(Y(0.85), (bottom - top) / max(1, n))
        for i, it in enumerate(items):
            y = top + i * gap
            out.append(_text(X(0.9), y + PX(6), f"{i+1:02d}", PX(20),
                             self.p["secondary"], bold=True))
            tx, _ = vtext(X(1.7), y, it, PX(16), self.p["text"],
                          max_w=X(10.5), max_h=Y(0.7))
            out.append(tx)
            out.append(line(X(0.9), y + gap - Y(0.06), X(12.3),
                            y + gap - Y(0.06), self.p["line"], 1))
        return out

    def _bullets(self, items, x, y, w, gap=Y(0.62)):
        out = []
        cy = y
        for it in items:
            head, detail = (it.split("|", 1) if "|" in it else (it, ""))
            out.append(rect(x, cy + PX(5), PX(5), PX(5), self.p["secondary"]))
            head_svg, head_y = vtext(x + X(0.3), cy, head, PX(15), self.p["text"],
                                     bold=True, max_w=w - X(0.4), max_h=gap * 0.62)
            out.append(head_svg)
            next_y = max(cy + gap, head_y)
            if detail:
                d_svg, d_y = vtext(x + X(0.3), cy + PX(20), detail, PX(12),
                                   self.p["muted"], max_w=w - X(0.4),
                                   max_h=gap * 0.5)
                out.append(d_svg)
                next_y = max(next_y, d_y)
            cy = next_y
        return "\n".join(out)

    def content(self, d):
        out = [self._bg(), self._title_bar(d.get("title", ""), d.get("subtitle"),
                                           d.get("num"), stype="content")]
        items = d.get("items", [])
        if d.get("columns", 1) == 2 and len(items) > 3:
            half = (len(items) + 1) // 2
            out.append(self._bullets(items[:half], X(0.9), Y(1.7), X(5.8)))
            out.append(self._bullets(items[half:], X(6.9), Y(1.7), X(5.8)))
        else:
            out.append(self._bullets(items, X(0.9), Y(1.7), X(11.5)))
        return out

    def two_column(self, d):
        out = [self._bg(), self._title_bar(d.get("title", ""), d.get("subtitle"),
                                           stype="two_column"),
               rect(X(0.6), Y(1.7), X(5.9), Y(4.8), self.p["surface"]),
               rect(X(6.8), Y(1.7), X(5.9), Y(4.8), self.p["surface"])]
        lt, _ = vtext(X(0.9), Y(1.9), d.get("left_title", "左栏"), PX(16),
                      self.p["primary"], bold=True, max_w=X(5.3), max_h=Y(0.5))
        out.append(lt)
        rt, _ = vtext(X(7.1), Y(1.9), d.get("right_title", "右栏"), PX(16),
                      self.p["primary"], bold=True, max_w=X(5.3), max_h=Y(0.5))
        out.append(rt)
        out.append(self._bullets(d.get("left", []), X(0.9), Y(2.5), X(5.3), Y(0.6)))
        out.append(self._bullets(d.get("right", []), X(7.1), Y(2.5), X(5.3), Y(0.6)))
        return out

    def table(self, d):
        out = [self._bg(), self._title_bar(d.get("title", ""), d.get("subtitle"),
                                           stype="table")]
        headers = d.get("headers", [])
        rows = d.get("rows", [])
        nrows = len(rows) + 1
        ncols = max(len(headers), *(len(r) for r in rows) if rows else [1])
        tx, ty = X(0.6), Y(1.7)
        tw, th = X(12.1), Y(4.8)
        cw = tw / ncols
        ch = th / nrows
        for j, h in enumerate(headers):
            out.append(rect(tx + j * cw, ty, cw, ch, self.p["primary"]))
            hsvg, _ = vtext(tx + j * cw + X(0.1), ty + ch * 0.12, str(h), PX(13),
                            "FFFFFF", bold=True, max_w=cw - X(0.2), max_h=ch * 0.76)
            out.append(hsvg)
        for i, row in enumerate(rows, 1):
            for j, val in enumerate(row):
                fill = self.p["surface"] if i % 2 else self.p["bg"]
                out.append(rect(tx + j * cw, ty + i * ch, cw, ch, fill))
                vsvg, _ = vtext(tx + j * cw + X(0.1), ty + i * ch + ch * 0.12,
                                str(val), PX(12), self.p["text"],
                                max_w=cw - X(0.2), max_h=ch * 0.76)
                out.append(vsvg)
        return out

    def chart(self, d):
        out = [self._bg(), self._title_bar(d.get("title", ""), d.get("subtitle"),
                                           stype="chart")]
        ctype = d.get("chart_type", "bar").lower()
        cats = d.get("categories", [])
        series = d.get("series", [])
        if not cats or not series:
            out.append(_text(W / 2, Y(4), "[ 无图表数据 ]", PX(14),
                             self.p["muted"], align="center"))
            return out
        emphasis = d.get("emphasis", [])
        if isinstance(emphasis, int):
            emphasis = [emphasis]
        ser_colors = [self.p["primary"], self.p["secondary"], self.p["accent"],
                      self.p["muted"]]

        def color_for(si):
            return ser_colors[si % len(ser_colors)]

        values = [v for s in series for v in s.get("values", [])]
        vmax = max(values) if values else 1
        vmax = max(vmax, 1)
        # plot frame
        px0, py0 = X(0.9), Y(1.9)
        pw, ph = X(11.5), Y(4.4)
        base = py0 + ph
        # horizontal gridlines + y-axis value labels (4 intervals)
        ng = 4
        for g in range(ng + 1):
            gy = base - (ph * g / ng)
            out.append(line(px0, gy, px0 + pw, gy, self.p["line"], 1))
            gv = vmax * g / ng
            out.append(_text(px0 - X(0.12), gy + PX(4), f"{gv:g}",
                             PX(11), self.p["muted"], align="right"))
        if ctype in ("bar", "horizontal"):
            n = len(cats)
            bh = ph / n * 0.6
            gap = ph / n
            for i, c in enumerate(cats):
                yy = py0 + i * gap + (gap - bh) / 2
                out.append(_text(px0, yy + bh * 0.25, c, PX(12), self.p["text"]))
                bw = (series[0]["values"][i] / vmax) * (pw - X(2.4))
                col = self.p["accent"] if i in emphasis else self.p["primary"]
                out.append(rect(px0 + X(1.9), yy, max(bw, 1), bh, col, rx=2))
                out.append(_text(px0 + X(1.9) + bw + X(0.1), yy + bh * 0.22,
                                 str(series[0]["values"][i]), PX(11),
                                 self.p["secondary"]))
        elif ctype in ("line",):
            n = len(cats)
            step = (pw - X(1.0)) / max(n - 1, 1)
            x0 = px0 + X(0.5)
            for si, ser in enumerate(series):
                pts = []
                for i, v in enumerate(ser.get("values", [])):
                    cx = x0 + i * step
                    cy = base - (v / vmax) * ph
                    pts.append((cx, cy))
                poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
                col = color_for(si)
                out.append(f'<polyline points="{poly}" fill="none" '
                           f'stroke="#{col}" stroke-width="2.5"/>')
                for i, (x, y) in enumerate(pts):
                    pc = self.p["accent"] if i in emphasis else col
                    out.append(circle(x, y, 4, pc))
                    if i in emphasis or (si == 0 and i == len(pts) - 1):
                        out.append(_text(x, y - PX(10), str(ser["values"][i]),
                                         PX(11), self.p["text"], align="center"))
            for i, c in enumerate(cats):
                out.append(_text(x0 + i * step, base + PX(16), c, PX(11),
                                 self.p["muted"], align="center"))
        else:  # column clustered (default), multi-series aware
            n = len(cats)
            m = len(series)
            slot = (pw - X(0.5)) / n
            group_w = slot * 0.7
            bar_w = group_w / m * 0.82
            for i, c in enumerate(cats):
                gx = px0 + X(0.3) + i * slot + (slot - group_w) / 2
                for si, ser in enumerate(series):
                    vals = ser.get("values", [])
                    v = vals[i] if i < len(vals) else 0
                    bh = (v / vmax) * (ph - PX(20))
                    bx = gx + si * (group_w / m) + (group_w / m - bar_w) / 2
                    col = self.p["accent"] if i in emphasis else color_for(si)
                    out.append(rect(bx, base - bh, bar_w, bh, col, rx=2))
                    out.append(_text(bx + bar_w / 2, base - bh - PX(4), str(v),
                                     PX(11), self.p["secondary"], align="center"))
                out.append(_text(gx + group_w / 2, base + PX(6), c, PX(11),
                                 self.p["muted"], align="center"))
        return out

    def timeline(self, d):
        out = [self._bg(), self._title_bar(d.get("title", ""), d.get("subtitle"),
                                           stype="timeline")]
        ms = d.get("milestones", [])
        if not ms:
            return out
        y = Y(4.0)
        out.append(line(X(1.0), y, X(12.3), y, self.p["line"], 2))
        n = len(ms)
        step = X(11.3) / n
        for i, m in enumerate(ms):
            cx = X(1.0) + step * (i + 0.5)
            out.append(rect(cx - PX(4), y - PX(4), PX(8), PX(8), self.p["primary"]))
            lab, _ = vtext(cx, y - Y(1.05), m.get("label", ""), PX(13),
                           self.p["primary"], bold=True, align="center",
                           max_w=min(step * 0.95, X(2.4)), max_h=Y(0.8))
            out.append(lab)
            desc, _ = vtext(cx, y + Y(0.15), m.get("desc", ""), PX(11),
                            self.p["muted"], align="center",
                            max_w=min(step * 0.95, X(2.4)), max_h=Y(0.8))
            out.append(desc)
        return out

    def quote(self, d):
        out = [self._bg(),
               self._icon(d.get("icon", "quote"), X(0.9), Y(1.7), PX(48)),
               _text(X(1.2), Y(1.7), "\u201C", PX(120), self.p["primary"], bold=True)]
        q, _ = vtext(X(1.5), Y(2.3), d.get("quote", ""), PX(26), self.p["text"],
                     italic=True, max_w=X(10.5), max_h=Y(2.6))
        out.append(q)
        if d.get("attribution"):
            a, _ = vtext(X(1.5), Y(5.2), f"— {d['attribution']}", PX(15),
                         self.p["secondary"], max_w=X(10.5), max_h=Y(0.6))
            out.append(a)
        return out

    def image(self, d):
        out = [self._bg(), self._title_bar(d.get("title", ""), d.get("subtitle"),
                                           stype="image")]
        path = d.get("image_path", "")
        x, y, w, h = X(1.2), Y(1.8), X(10.9), Y(4.6)
        if path and os.path.exists(path):
            out.append(f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                       f'href="{esc(path)}"/>')
        else:
            out.append(rect(x, y, w, h, self.p["surface"], stroke=self.p["line"]))
            out.append(_text(x + w / 2, y + h / 2, "[ 图片占位 ]", PX(14),
                             self.p["muted"], align="center"))
        return out

    def summary(self, d):
        out = [self._bg(), self._title_bar(d.get("title", "总结"), stype="summary"),
               self._bullets(d.get("points", []), X(0.9), Y(1.7), X(11.5), Y(0.66))]
        if d.get("conclusion"):
            out.append(rect(X(0.9), Y(6.0), X(11.5), Y(0.9), self.p["primary"]))
            c, _ = vtext(X(1.1), Y(6.05), d["conclusion"], PX(15), "FFFFFF",
                         bold=True, max_w=X(11.1), max_h=Y(0.8))
            out.append(c)
        return out

    def bullets(self, d):
        out = [self._bg(), self._title_bar(d.get("title", ""), d.get("subtitle"),
                                           stype="bullets"),
               self._bullets(d.get("items", []), X(0.9), Y(1.7), X(11.5), Y(0.66))]
        return out

    def contact(self, d):
        out = [self._bg()]
        out.append(self._icon(d.get("icon", "mail"), W / 2 - PX(24), Y(1.4), PX(48)))
        t, _ = vtext(W / 2, Y(2.4), d.get("title", "联系我们"), PX(36),
                     self.p["primary"], bold=True, align="center",
                     max_w=X(11.3), max_h=Y(1.0))
        out.append(t)
        info, _ = vtext(W / 2, Y(3.6), d.get("info", ""), PX(16), self.p["text"],
                        align="center", max_w=X(11.3), max_h=Y(2.0))
        out.append(info)
        return out

    RENDERERS = {
        "cover": cover, "section": section, "agenda": agenda, "content": content,
        "two_column": two_column, "table": table, "chart": chart, "timeline": timeline,
        "quote": quote, "image": image, "summary": summary, "bullets": bullets,
        "contact": contact,
    }

    def render(self, slide: dict) -> str:
        stype = slide.get("type", "content")
        fn = self.RENDERERS.get(stype, self.content)
        frags = fn(self, slide)
        body = "\n  ".join(frags)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n  {body}\n</svg>')


# ---------------------------------------------------------------------------
# Project scaffolding + conversion
# ---------------------------------------------------------------------------
def footer_svg(pal: dict, idx: int, footer: str, page_numbers: bool) -> str:
    out = []
    if footer:
        out.append(_text(X(0.5), Y(7.05), footer, PX(9), pal["muted"]))
    if page_numbers:
        out.append(_text(X(12.3), Y(7.05), str(idx), PX(9), pal["muted"],
                         align="right"))
    return "\n  ".join(out)


def build_project(brief: dict, project_dir: Path, pal: dict, footer: str,
                  page_numbers: bool) -> None:
    (project_dir / "svg_output").mkdir(parents=True, exist_ok=True)
    slides = brief.get("slides", [])
    for i, sl in enumerate(slides, 1):
        svg = SvgSlide(pal).render(sl)
        if sl.get("type") not in ("cover", "section") and (footer or page_numbers):
            svg = svg.replace("</svg>", f"  {footer_svg(pal, i, footer, page_numbers)}\n</svg>")
        (project_dir / "svg_output" / f"page_{i:03d}.svg").write_text(
            svg, encoding="utf-8")
    spec = f"""# spec_lock

## pptx_structure
- mode: flat

## typography
- font_family: {pal['font']}
- title: 44
- body: 18

## colors
- bg: {pal['bg']}
- text: {pal['text']}
- primary: {pal['primary']}
- secondary: {pal['secondary']}
- surface: {pal['surface']}
- accent: {pal['accent']}
- line: {pal['line']}
- muted: {pal['muted']}
"""
    (project_dir / "spec_lock.md").write_text(spec, encoding="utf-8")


def _scripts_dir(base: Path | None) -> Path | None:
    """Return the dir that directly contains svg_to_pptx.py, or None."""
    if not base:
        return None
    if (base / "svg_to_pptx.py").exists():
        return base
    if (base / "scripts" / "svg_to_pptx.py").exists():
        return base / "scripts"
    return None


def run_convert(project_dir: Path, scripts_dir: Path, python_exe: str) -> Path:
    script = scripts_dir / "svg_to_pptx.py"
    if not script.exists():
        raise FileNotFoundError(f"ppt-master converter not found: {script}")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [python_exe, str(script), str(project_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(scripts_dir), env=env,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + "\n" + proc.stderr + "\n")
        raise RuntimeError(f"svg_to_pptx failed (exit {proc.returncode})")
    exports = list((project_dir / "exports").glob("*.pptx"))
    if not exports:
        raise RuntimeError("svg_to_pptx produced no .pptx output")
    return exports[0]


def locate_ppt_master(explicit: str | None) -> Path:
    here = Path(__file__).resolve().parent
    bundled = here.parent / "vendor" / "ppt-master-scripts"
    candidates = [
        Path(explicit) if explicit else None,
        Path(os.environ.get("PPT_MASTER_DIR", "")) if os.environ.get("PPT_MASTER_DIR") else None,
        bundled,
        Path.home() / ".workbuddy" / "skills" / "ppt-master" / "skills" / "ppt-master",
        Path.home() / ".claude" / "skills" / "ppt-master" / "skills" / "ppt-master",
        Path("/root/.workbuddy/skills/ppt-master/skills/ppt-master"),
    ]
    for c in candidates:
        sd = _scripts_dir(c)
        if sd:
            return sd
    raise FileNotFoundError(
        "ppt-master not found. Unzip vendor/ppt-master-scripts (bundled) or "
        "install the ppt-master skill, or pass --ppt-master <dir>.")


def main():
    ap = argparse.ArgumentParser(
        description="PPT Pro Studio — primary ppt-master SVG->PPTX render path")
    ap.add_argument("brief", help="path to brief JSON")
    ap.add_argument("--out", default="hifi.pptx", help="output .pptx path")
    ap.add_argument("--ppt-master", default=None, help="ppt-master skill directory")
    ap.add_argument("--python", default=sys.executable, help="python3 interpreter")
    ap.add_argument("--keep-project", default=None,
                    help="keep the intermediate ppt-master project at this dir")
    ap.add_argument("--no-transition", action="store_true",
                    help="skip random page-transition injection")
    ap.add_argument("--seed", type=int, default=None,
                    help="random seed for transition effects")
    ap.add_argument("--transition-duration", type=float, default=0.5)
    args = ap.parse_args()

    with open(args.brief, "r", encoding="utf-8") as f:
        brief = json.load(f)

    style = brief.get("style", "tech_dark")
    pal = PALETTES.get(style, PALETTES["tech_dark"])
    footer = brief.get("footer", "")
    page_numbers = brief.get("page_numbers", True)

    ppt_master_dir = locate_ppt_master(args.ppt_master)

    tmp = None
    if args.keep_project:
        project_dir = Path(args.keep_project)
        project_dir.mkdir(parents=True, exist_ok=True)
    else:
        tmp = tempfile.mkdtemp(prefix="ppt_hifi_")
        project_dir = Path(tmp) / "project"
        project_dir.mkdir(parents=True, exist_ok=True)

    build_project(brief, project_dir, pal, footer, page_numbers)
    pptx = run_convert(project_dir, ppt_master_dir, args.python)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pptx, out_path)

    transitions = False
    if not args.no_transition:
        try:
            from add_transitions import add_random_transitions
            add_random_transitions(out_path, seed=args.seed,
                                   duration=args.transition_duration)
            transitions = True
        except Exception as e:  # transition is best-effort, never fatal
            sys.stderr.write(f"warning: transitions skipped: {e}\n")

    if tmp and not args.keep_project:
        shutil.rmtree(tmp, ignore_errors=True)

    print(json.dumps({"ok": True, "file": str(out_path.resolve()),
                      "engine": "ppt-master SVG->PPTX (hugohe3/ppt-master, 16.6k★)",
                      "slides": len(brief.get("slides", [])),
                      "transitions": transitions,
                      "style": style}, ensure_ascii=False))


if __name__ == "__main__":
    main()
