# PPT Pro Studio

> 专业级 PPT 生产工作流技能 · 商用 · 可变现 · **零限制**

把一句模糊的需求，变成一份能直接拿去给客户演示、能上传知识付费平台售卖的
**可编辑、无水印、可离线** `.pptx`。

- **License**: MIT（含引用的子技能均为 MIT / MIT-0，无 AGPL / 无 copyleft 义务）
- **No network at render time** · **No watermarks** · **Fully editable** (native shapes/charts)
- **Callable by anyone**: skill-compatible agents, OR any MCP-capable LLM via `ppt-studio-mcp`

## What's inside

| Path | What |
|------|------|
| `SKILL.md` | The orchestration workflow (prompt-enhancement FIRST → outline → design → render → QA → export). For any skill-compatible agent. |
| `scripts/ppt_master_hifi.py` | **Primary** renderer: brief → high-fidelity SVG → ppt-master `svg_to_pptx` → native `.pptx` + random page transitions. Wraps the highest-starred PPTX skill (hugohe3/ppt-master, 16.6k★, MIT). |
| `scripts/ppt_studio_generate.py` | **Fallback** deterministic python-pptx renderer. P3-6 pre-calculation overflow control, 13 slide types, native charts, image+text mixed layout, speaker notes. |
| `scripts/ppt_marp.py` | **Showcase** renderer: brief → Marp Markdown → HTML/PDF/PPTX (visual ceiling for presentations/roadshows). |
| `scripts/generate.py` | **Unified entry**: routes by `brief.delivery` — `editable` → core engine, `showcase` → Marp HTML. |
| `scripts/template_market.py` | **Template market** CLI: 10 industry templates (pitch, course, annual review, product launch, XHS, gov, medical, e-com, guochao, fintech). |
| `scripts/theme_market.py` | **Theme market** CLI + loader: 12 themes, `list` / `show` / `validate` / `init`. |
| `scripts/prompt_enhance.py` | Offline brief scaffolder with narrative structure (persuade/inform/teach/inspire) + delivery routing. |
| `scripts/qa2.py` | QA 2.1 layout audit: bounds, placeholders, font floor, CJK font, WCAG contrast, truncation, image upscale, HTML path audit, score. |
| `scripts/collab.py` | Collaboration: `serve` (LAN preview), `export` (brief→Markdown for Lexiang/Tencent Docs), `init` (git project scaffold). |
| `scripts/add_transitions.py` | Injects random per-slide transitions via ppt-master's OOXML transition core. |
| `scripts/icons.py` | Embedded offline icon library (~50 vector icons, OOXML `custGeom`, WPS-editable). |
| `ui/console.html` | **UI Console** (P3-10): zero-dependency local web form — template picker, theme cards, narrative dropdown, live slide preview, one-click brief export. |
| `vendor/ppt-master-scripts/` | Bundled ppt-master v3.1.0 converter + transition core (offline, MIT). |
| `mcp-server/ppt-studio-mcp.js` | Zero-dependency MCP server (stdio). Tools: `generate_ppt`, `qa_check`, `list_styles`, `list_templates`. |
| `references/prompt-refiner-PROMPT.md` | The mandatory first-step prompt-enhancer (MIT, from xie-maker/prompt-refiner-skill). |
| `references/design-system.md` | Palettes + typography + field mapping (12 themes, 8pt grid). |
| `references/qa-checklist.md` | Quality gate. |
| `examples/sample-brief.json` | Example input (14 slides, demonstrates `media` + `notes` + theme). |
| `themes/` | Theme market: 12 selectable palettes as standalone JSON (add your own). |
| `templates/` | Template market: 10 industry templates as standalone JSON. |
| `COLLABORATION.md` | Collaboration guide: git versioning, LAN preview, Lexiang/Tencent Docs import. |

## The pipeline (always serial)

```
① Prompt Enhancement (MANDATORY) → ② Brief → ③ Outline → ④ Design
        → ⑤ Content → ⑥ Render (delivery-routed) → ⑦ QA Gate → ⑧ Refine → ⑨ Export
```

Step ① uses the **Prompt Refiner** method to turn "做个 AI 的 PPT" into a structured
brief (audience, goal, narrative, delivery, style, length, sections, constraints, acceptance).
Skipping it is a workflow failure — vague input yields low-quality output.

Step ⑥ routes by `brief.delivery`: `editable` (default) → core engine (native .pptx);
`showcase` → Marp HTML (visual ceiling).

## Render engines

**Unified entry (recommended):**
```bash
python3 scripts/generate.py brief.json --out deck.pptx   # delivery=editable (default)
python3 scripts/generate.py brief.json --out deck.html   # delivery=showcase
```

**Primary (editable · highest-starred PPTX skill · with page-flip animations):**
`python3 scripts/ppt_master_hifi.py brief.json --out deck.pptx`
— renders brief → high-fidelity vector SVG → ppt-master `svg_to_pptx` → native editable `.pptx`,
then injects **random per-slide transitions**. All text auto-wraps & shrinks inside the canvas (no overflow).
The ppt-master converter is **bundled offline** in `vendor/ppt-master-scripts/` — no separate install.

**Fallback (deterministic · P3-6 pre-calculation overflow control):** `python3 scripts/ppt_studio_generate.py brief.json --out deck.pptx`
— pure python-pptx, pre-calculated font sizing for bullets & table cells (no unreliable TEXT_TO_FIT_SHAPE),
dynamic line spacing + transitions. Auto-used if the primary path is unavailable.

**Showcase (visual ceiling · Marp):** `python3 scripts/ppt_marp.py brief.json --out deck.html [--pdf] [--pptx]`
— brief → Marp Markdown (theme CSS auto-generated) → self-contained HTML. Optional PDF/PPTX if Chromium available.

Universal: connect `ppt-studio-mcp` and call `generate_ppt` (internally routes by delivery: showcase→Marp, editable→primary→fallback).

## P3 capabilities (v1.2.0)

- **Template Market** — 10 industry templates: startup pitch, course lecture, annual review,
  product launch, XHS knowledge card, gov report, medical science, e-com promo, guochao brand,
  fintech report. `python3 scripts/template_market.py list` to browse; `apply <id> --out brief.json` to scaffold.
- **Narrative Structure** — 4 skeletons (persuade/inform/teach/inspire), each with a per-page
  type mapping. Auto-selected from goal; overridable via brief `narrative` field.
- **Delivery Routing** — `editable` (default, core engine → native .pptx) vs `showcase` (Marp → visual HTML).
  Auto-detected from user intent; overridable via brief `delivery` field.
- **Theme Market** — 12 bundled, editable themes in `themes/` (incl. `fintech_green`,
  `sunset_orange`, `mono_ink`, `guochao_red`, `medical_blue`, `ecommerce_orange`, `gov_red`).
- **UI Console** — `ui/console.html`: zero-dependency local web form with template picker,
  theme cards, narrative dropdown, live slide preview, one-click brief export.
- **Collaboration** — `scripts/collab.py`: git versioning (`init`), LAN preview (`serve`),
  brief→Markdown export for Lexiang/Tencent Docs import (`export`). See `COLLABORATION.md`.
- **QA 2.1** — CJK font detection, WCAG contrast, truncation verification, image upscale check,
  HTML path audit. `python3 scripts/qa2.py deck.pptx` or `--html deck.html`.
- **P3-6 Overflow Pre-calculation** — fallback engine pre-calculates bullet & table cell
  font sizes before rendering, replacing unreliable `TEXT_TO_FIT_SHAPE`.

## Components & licenses (all permissive)

| Role | Component | License |
|------|-----------|---------|
| Prompt enhancement (step ①) | prompt-refiner-skill | MIT |
| Prompt enhancement (alt) | prompt-optimize (Alpha-Prompt, local) | local skill |
| **Primary renderer** | **ppt_master_hifi.py → ppt-master** | MIT (16.6k★) |
| Fallback renderer | ppt_studio_generate.py (this skill) | MIT-0 |
| Showcase renderer | ppt_marp.py + Marp CLI | MIT |
| Transition injector | add_transitions.py (this skill) | MIT-0 |
| Universal MCP | ppt-studio-mcp (this skill) | MIT |

> ⚠️ Excluded on purpose: `linshenkx/prompt-optimizer` (26.5k★) is **AGPL-3.0** —
> a strong copyleft license incompatible with a commercial/monetizable, no-restriction
> distribution. Do NOT add AGPL components to this studio.

See `INSTALL.md` for setup in WorkBuddy, Claude Code, Cursor, or any MCP client.
