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
| `scripts/ppt_studio_generate.py` | Deterministic python-pptx renderer. 5 palettes, 12 slide types, native charts. |
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

Primary: `python3 scripts/ppt_studio_generate.py brief.json --out deck.pptx`
Premium (high-fidelity true .pptx + animations): the `ppt-master` skill (MIT, separately installed).
**Premium SVG→PPTX (optional button ⑥-B)**: `python3 scripts/ppt_master_hifi.py brief.json --out deck.pptx`
— a self-contained wrapper that renders brief → high-fidelity SVG → ppt-master `svg_to_pptx` → native `.pptx`
(requires the `ppt-master` skill installed at `~/.workbuddy/skills/ppt-master`).
Universal: connect `ppt-studio-mcp` and call `generate_ppt`.

## Components & licenses (all permissive)

| Role | Component | License |
|------|-----------|---------|
| Prompt enhancement (step ①) | prompt-refiner-skill | MIT |
| Prompt enhancement (alt) | prompt-optimize (Alpha-Prompt, local) | local skill |
| Primary renderer | ppt_studio_generate.py (this skill) | MIT-0 |
| Alt renderer | pptx-generator | MIT-0 |
| Premium renderer | ppt-master | MIT |
| Premium SVG→PPTX wrapper | ppt_master_hifi.py (this skill) | MIT |
| Universal MCP | ppt-studio-mcp (this skill) | MIT |

> ⚠️ Excluded on purpose: `linshenkx/prompt-optimizer` (26.5k★) is **AGPL-3.0** —
> a strong copyleft license incompatible with a commercial/monetizable, no-restriction
> distribution. Do NOT add AGPL components to this studio.

See `INSTALL.md` for setup in WorkBuddy, Claude Code, Cursor, or any MCP client.
