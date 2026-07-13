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
| `scripts/ppt_studio_generate.py` | **Fallback** deterministic python-pptx renderer. 5 palettes, 12 slide types, native charts, overflow-safe auto-fit. |
| `scripts/add_transitions.py` | Injects random per-slide transitions via ppt-master's OOXML transition core. |
| `scripts/qa2.py` | QA 2.0 layout audit: bounds, placeholders, font floor (≥11pt), transitions, icons, brand theme, score. |
| `vendor/ppt-master-scripts/` | Bundled ppt-master converter + transition core (offline, MIT). |
| `mcp-server/ppt-studio-mcp.js` | Zero-dependency MCP server (stdio). Tools: `generate_ppt`, `qa_check`, `list_styles`. |
| `references/prompt-refiner-PROMPT.md` | The mandatory first-step prompt-enhancer (MIT, from xie-maker/prompt-refiner-skill). |
| `references/design-system.md` | Palettes + typography + field mapping. |
| `references/qa-checklist.md` | Quality gate. |
| `examples/sample-brief.json` | Example input. |

## The pipeline (always serial)

```
① Prompt Enhancement (MANDATORY) → ② Brief → ③ Outline → ④ Design
        → ⑤ Content → ⑥ Render (.pptx) → ⑦ QA Gate → ⑧ Refine → ⑨ Export
```

Step ① uses the **Prompt Refiner** method to turn "做个 AI 的 PPT" into a structured
brief (audience, goal, style, length, sections, constraints, acceptance). Skipping
it is a workflow failure — vague input yields low-quality output.

## Render engine

**Primary (recommended · highest-starred PPTX skill · with page-flip animations):**
`python3 scripts/ppt_master_hifi.py brief.json --out deck.pptx`
— renders brief → high-fidelity vector SVG → ppt-master `svg_to_pptx` → native editable `.pptx`,
then injects **random per-slide transitions**. All text auto-wraps & shrinks inside the canvas (no overflow).
The ppt-master converter is **bundled offline** in `vendor/ppt-master-scripts/` — no separate install.

**Fallback (deterministic · zero extra deps):** `python3 scripts/ppt_studio_generate.py brief.json --out deck.pptx`
— pure python-pptx, `TEXT_TO_FIT_SHAPE` auto-fit + dynamic line spacing + transitions. Auto-used if the primary path is unavailable.

Universal: connect `ppt-studio-mcp` and call `generate_ppt` (internally primary→fallback).

## Components & licenses (all permissive)

| Role | Component | License |
|------|-----------|---------|
| Prompt enhancement (step ①) | prompt-refiner-skill | MIT |
| Prompt enhancement (alt) | prompt-optimize (Alpha-Prompt, local) | local skill |
| **Primary renderer** | **ppt_master_hifi.py → ppt-master** | MIT (16.6k★) |
| Fallback renderer | ppt_studio_generate.py (this skill) | MIT-0 |
| Transition injector | add_transitions.py (this skill) | MIT-0 |
| Universal MCP | ppt-studio-mcp (this skill) | MIT |

> ⚠️ Excluded on purpose: `linshenkx/prompt-optimizer` (26.5k★) is **AGPL-3.0** —
> a strong copyleft license incompatible with a commercial/monetizable, no-restriction
> distribution. Do NOT add AGPL components to this studio.

See `INSTALL.md` for setup in WorkBuddy, Claude Code, Cursor, or any MCP client.
