#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
icons.py — offline, dependency-free linear icon set for PPT Pro Studio.

Icons are stored as normalized polylines in a 0..100 coordinate space
(one or more strokes per icon). Two renderers are provided:

  * icon_svg(name, x, y, size_px, color_hex, stroke_px) -> SVG fragment
        Used by the ppt-master (hifi) engine: the path is authored directly
        into the page SVG and converted to a native editable vector shape.

  * add_icon_to_slide(slide, name, x, y, size_in, color_hex, stroke_w_pt)
        Used by the python-pptx engine: builds an OOXML <a:custGeom> custom
        geometry (no fill, colored outline). Native, editable, WPS-compatible,
        and needs no bitmap renderer (cairo/svglib) at all.

All icons are MIT-0 / public-domain style simple line geometry.
"""
from __future__ import annotations

import math
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


def _circle(cx, cy, r, n=24, close=True):
    pts = [(cx + r * math.cos(2 * math.pi * i / n),
            cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    if close:
        pts.append(pts[0])
    return pts


def _star(points=5, outer=46, inner=19, cx=50, cy=50):
    pts = []
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        r = outer if i % 2 == 0 else inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    pts.append(pts[0])
    return pts


def _poly(*pts):
    return [tuple(p) for p in pts]


# name -> list[stroke]; stroke = list[(x,y)] in 0..100 space.
ICONS = {
    # --- arrows / actions ---
    "arrow-right": [_poly((15, 50), (85, 50)),
                    _poly((62, 28), (85, 50), (62, 72))],
    "arrow-up-right": [_poly((30, 70), (70, 30)),
                       _poly((38, 30), (70, 30), (70, 62))],
    "check": [_poly((20, 52), (42, 73), (82, 27))],
    "x": [_poly((26, 26), (74, 74)), _poly((74, 26), (26, 74))],
    "plus": [_poly((50, 18), (50, 82)), _poly((18, 50), (82, 50))],
    "minus": [_poly((18, 50), (82, 50))],
    # --- shapes ---
    "circle": [_circle(50, 50, 34)],
    "square": [_poly((24, 24), (76, 24), (76, 76), (24, 76), (24, 24))],
    "triangle": [_poly((50, 20), (80, 76), (20, 76), (50, 20))],
    "diamond": [_poly((50, 14), (86, 50), (50, 86), (14, 50), (50, 14))],
    "star": [_star()],
    "heart": [_poly((50, 78), (22, 50), (22, 32), (38, 24), (50, 36),
                    (62, 24), (78, 32), (78, 50), (50, 78))],
    # --- brand-ish / concept ---
    "bolt": [_poly((56, 14), (34, 54), (50, 54), (44, 86), (72, 42),
                   (54, 42), (56, 14))],
    "flag": [_poly((32, 18), (32, 82)),
             _poly((32, 20), (70, 20), (58, 38), (32, 38))],
    "bookmark": [_poly((30, 18), (70, 18), (70, 82), (50, 66), (30, 82),
                       (30, 18))],
    "tag": [_poly((22, 34), (52, 20), (80, 48), (66, 78), (22, 78),
                  (22, 34)), _circle(38, 40, 6)],
    "target": [_circle(50, 50, 36), _circle(50, 50, 22), _circle(50, 50, 8)],
    "search": [_circle(44, 44, 26), _poly((62, 62), (84, 84))],
    "settings": [_poly((22, 36), (78, 36)), _circle(50, 36, 9),
                 _poly((22, 64), (78, 64)), _circle(50, 64, 9)],
    "sliders": [_poly((20, 30), (80, 30)), _circle(60, 30, 8),
                _poly((20, 50), (80, 50)), _circle(36, 50, 8),
                _poly((20, 70), (80, 70)), _circle(64, 70, 8)],
    # --- people ---
    "user": [_circle(50, 32, 16),
             _poly((22, 82), (28, 58), (50, 58), (72, 58), (78, 82), (22, 82))],
    "users": [_circle(38, 36, 13), _circle(66, 36, 13),
              _poly((14, 82), (20, 60), (38, 60), (40, 70), (40, 82), (14, 82)),
              _poly((86, 82), (80, 60), (62, 60), (60, 70), (60, 82), (86, 82))],
    # --- comms ---
    "mail": [_poly((20, 30), (80, 30), (80, 70), (20, 70), (20, 30)),
             _poly((20, 30), (50, 52), (80, 30))],
    "phone": [_poly((30, 20), (42, 20), (46, 34), (56, 30), (62, 42),
                    (50, 48), (54, 62), (42, 66), (30, 56), (34, 44), (30, 20))],
    "calendar": [_poly((22, 30), (78, 30), (78, 78), (22, 78), (22, 30)),
                 _poly((22, 30), (22, 20), (34, 20), (34, 30)),
                 _poly((66, 30), (66, 20), (78, 20), (78, 30)),
                 _poly((22, 44), (78, 44))],
    "clock": [_circle(50, 50, 34), _poly((50, 50), (50, 26)),
              _poly((50, 50), (70, 50))],
    "map-pin": [_poly((50, 14), (76, 56), (50, 86), (24, 56), (50, 14)),
                _circle(50, 50, 10)],
    # --- status ---
    "info": [_circle(50, 50, 36), _poly((50, 40), (50, 70)),
             _circle(50, 30, 3)],
    "warning": [_poly((50, 18), (82, 76), (18, 76), (50, 18)),
                _poly((50, 40), (50, 60)), _circle(50, 68, 3)],
    "check-circle": [_circle(50, 50, 36), _poly((32, 52), (46, 66), (70, 36))],
    # --- content ---
    "quote": [_poly((24, 24), (24, 56), (44, 56)), _poly((56, 24), (56, 56),
                                                                 (76, 56))],
    "book": [_poly((28, 20), (28, 80), (72, 80), (72, 20)),
             _poly((28, 20), (50, 30), (72, 20))],
    "lightbulb": [_circle(50, 40, 22),
                  _poly((42, 64), (58, 64), (56, 76), (44, 76), (42, 64))],
    "rocket": [_poly((40, 14), (60, 20), (58, 54), (42, 54), (40, 14)),
               _poly((42, 54), (34, 70), (44, 64)),
               _poly((58, 54), (66, 70), (56, 64)), _circle(50, 30, 6)],
    "trophy": [_poly((30, 20), (70, 20), (64, 56), (36, 56), (30, 20)),
               _poly((36, 56), (36, 74), (64, 74), (64, 56)),
               _poly((30, 28), (20, 40), (22, 54), (30, 48)),
               _poly((70, 28), (80, 40), (78, 54), (70, 48))],
    "shield": [_poly((50, 16), (78, 28), (78, 52), (50, 84), (22, 52),
                     (22, 28), (50, 16)), _poly((42, 46), (48, 56), (62, 38))],
    "cloud": [_poly((34, 64), (24, 64), (24, 48), (34, 44), (40, 32),
                    (58, 32), (66, 44), (78, 48), (78, 64), (34, 64))],
    "link": [_poly((52, 30), (44, 30), (44, 44), (56, 44), (56, 58),
                   (44, 58), (44, 70), (68, 70), (68, 56), (56, 56),
                   (56, 42), (68, 42), (68, 30), (52, 30)),
             _circle(44, 50, 8), _circle(68, 50, 8)],
    "image": [_poly((20, 26), (80, 26), (80, 74), (20, 74), (20, 26)),
              _circle(38, 42, 8), _poly((20, 64), (42, 44), (58, 58),
                                        (72, 46), (80, 54))],
    "play": [_poly((34, 24), (34, 76), (76, 50), (34, 24))],
    "pause": [_poly((34, 24), (46, 24), (46, 76), (34, 76), (34, 24)),
              _poly((54, 24), (66, 24), (66, 76), (54, 76), (54, 24))],
    "code": [_poly((42, 28), (24, 50), (42, 72)),
             _poly((58, 28), (76, 50), (58, 72))],
    "database": [_poly((24, 30), (76, 30)), _circle(50, 30, 26),
                 _poly((24, 30), (24, 54), (76, 54), (76, 30)),
                 _poly((24, 54), (24, 70), (76, 70), (76, 54))],
    "filter": [_poly((22, 26), (78, 26), (54, 52), (54, 78), (46, 78),
                     (46, 52), (22, 26))],
    "layers": [_poly((50, 18), (80, 34), (50, 50), (20, 34), (50, 18)),
               _poly((20, 46), (50, 62), (80, 46)),
               _poly((20, 58), (50, 74), (80, 58))],
    "grid": [_poly((26, 26), (74, 26), (74, 74), (26, 74), (26, 26)),
             _poly((50, 26), (50, 74)), _poly((26, 50), (74, 50))],
    "compass": [_circle(50, 50, 36), _poly((50, 30), (58, 50), (50, 70),
                                           (42, 50), (50, 30))],
    "send": [_poly((26, 40), (74, 22), (56, 70), (48, 52), (26, 40))],
    "globe": [_circle(50, 50, 36), _poly((14, 50), (86, 50)),
              _poly((50, 14), (50, 86)),
              _poly((24, 30), (40, 24), (50, 30), (60, 24), (76, 30)),
              _poly((24, 70), (40, 76), (50, 70), (60, 76), (76, 70))],
    # --- data ---
    "chart-bar": [_poly((20, 74), (20, 26)), _poly((20, 74), (80, 74)),
                  _poly((30, 74), (30, 50)), _poly((46, 74), (46, 36)),
                  _poly((62, 74), (62, 56)), _poly((78, 74), (78, 30))],
    "chart-line": [_poly((18, 76), (82, 76)), _poly((18, 76), (18, 24)),
                   _poly((24, 56), (42, 38), (58, 50), (80, 26))],
    "pie": [_circle(50, 50, 36),
            _poly((50, 50), (50, 14), (80, 34), (50, 50))],
    "list": [_poly((30, 30), (76, 30)), _poly((30, 50), (76, 50)),
             _poly((30, 70), (76, 70)), _circle(20, 30, 4), _circle(20, 50, 4),
             _circle(20, 70, 4)],
    "columns": [_poly((24, 24), (46, 24), (46, 76), (24, 76), (24, 24)),
                _poly((54, 24), (76, 24), (76, 76), (54, 76), (54, 24))],
    "table": [_poly((20, 28), (80, 28), (80, 72), (20, 72), (20, 28)),
              _poly((20, 48), (80, 48)), _poly((44, 28), (44, 72)),
              _poly((62, 28), (62, 72))],
}

# Default icon per slide type (auto-placed by the engines).
DEFAULT_ICON = {
    "cover": "rocket",
    "section": "bookmark",
    "agenda": "list",
    "content": "list",
    "two_column": "columns",
    "table": "table",
    "chart": "chart-bar",
    "timeline": "clock",
    "quote": "quote",
    "image": "image",
    "summary": "check-circle",
    "bullets": "list",
    "contact": "mail",
}


# ---------------------------------------------------------------------------
# SVG renderer (hifi / ppt-master engine)
# ---------------------------------------------------------------------------
def icon_svg(name, x, y, size_px, color_hex, stroke_px=3.0):
    strokes = ICONS.get(name)
    if not strokes:
        return ""
    parts = []
    for st in strokes:
        d = "M " + " L ".join(f"{px * size_px / 100:.1f} {py * size_px / 100:.1f}"
                              for px, py in st)
        if len(st) > 1 and st[0] == st[-1]:
            d += " Z"
        parts.append(
            f'<path d="{d}" fill="none" stroke="#{color_hex}" '
            f'stroke-width="{stroke_px:.1f}" stroke-linejoin="round" '
            f'stroke-linecap="round"/>')
    return (f'<g transform="translate({x:.1f},{y:.1f})">'
            f'{"".join(parts)}</g>')


# ---------------------------------------------------------------------------
# OOXML custGeom renderer (python-pptx engine) — native, WPS-safe, no bitmaps
# ---------------------------------------------------------------------------
def _build_cust_geom(sp, strokes):
    spPr = sp._element.spPr
    for el in spPr.findall(qn("a:prstGeom")):
        spPr.remove(el)
    cust = spPr.makeelement(qn("a:custGeom"), {})
    spPr.append(cust)
    path_lst = cust.makeelement(qn("a:pathLst"), {})
    cust.append(path_lst)
    for st in strokes:
        path = cust.makeelement(qn("a:path"), {"w": "100000", "h": "100000"})
        path_lst.append(path)
        mt = path.makeelement(qn("a:moveTo"), {})
        pt = mt.makeelement(qn("a:pt"),
                            {"x": str(int(st[0][0] * 1000)),
                             "y": str(int(st[0][1] * 1000))})
        mt.append(pt)
        path.append(mt)
        for p in st[1:]:
            ln = path.makeelement(qn("a:lnTo"), {})
            pt = ln.makeelement(qn("a:pt"),
                                {"x": str(int(p[0] * 1000)),
                                 "y": str(int(p[1] * 1000))})
            ln.append(pt)
            path.append(ln)
        if len(st) > 1 and st[0] == st[-1]:
            path.append(path.makeelement(qn("a:close"), {}))


def add_icon_to_slide(slide, name, x, y, size_in, color_hex, stroke_w_pt=1.5):
    strokes = ICONS.get(name)
    if not strokes:
        return
    sp = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
        Inches(size_in), Inches(size_in))
    sp.fill.background()
    sp.line.color.rgb = RGBColor.from_string(color_hex)
    sp.line.width = Pt(stroke_w_pt)
    sp.shadow.inherit = False
    _build_cust_geom(sp, strokes)
    return sp
