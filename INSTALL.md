# Install & Call — PPT Pro Studio

This studio is **universal**: any user, any agent, any AI/LLM can install and call it.
No lock-in, no account, no API key required for rendering.

---

## A. As a Skill (WorkBuddy / Claude Code / Cursor / Codex)

### WorkBuddy
Skills in `~/.workbuddy/skills/` are auto-discovered. Copy the folder:

```bash
cp -r ppt-pro-studio ~/.workbuddy/skills/
```

Then invoke: "用 ppt-pro-studio 做一个关于 [主题] 的 PPT" or `/ppt-pro-studio`.

### Claude Code / Cursor / Codex
Copy to the agent's skills dir:

```bash
# Claude Code
cp -r ppt-pro-studio ~/.claude/skills/ppt-pro-studio
# Cursor
cp -r ppt-pro-studio ~/.cursor/skills/ppt-pro-studio
```

The agent reads `SKILL.md` and follows the pipeline. Ensure `python3` is on PATH
(set `PPT_STUDIO_PYTHON` env if not).

---

## B. As an MCP Server (any MCP-capable LLM)

No skill file needed — the model calls tools directly.

### 1. Register the server

Add to your MCP client config (Claude Desktop, Cursor, any MCP host):

```json
{
  "mcpServers": {
    "ppt-studio": {
      "command": "node",
      "args": ["/absolute/path/to/ppt-pro-studio/mcp-server/ppt-studio-mcp.js"]
    }
  }
}
```

> The server is **zero-dependency** — just `node`. No `npm install` required.

### 2. Call the tools

**generate_ppt** — render a brief into .pptx:
```json
{
  "brief": {
    "style": "tech_dark",
    "slides": [
      { "type": "cover", "title": "My Deck", "subtitle": "Subtitle" },
      { "type": "content", "title": "Points", "items": ["A", "B", "C"] },
      { "type": "chart", "title": "Growth", "chart_type": "bar",
        "categories": ["Q1","Q2"], "series": [{"name":"Rev","values":[10,20]}] }
    ]
  },
  "out": "./deck.pptx"
}
```

**qa_check** — validate a .pptx:
```json
{ "pptx_path": "./deck.pptx" }
```

**list_styles** — list palettes:
```json
{}
```

---

## C. CLI (direct)

Primary (ppt-master SVG→PPTX, recommended):
```bash
python3 ppt-pro-studio/scripts/ppt_master_hifi.py examples/sample-brief.json --out deck.pptx
```

Fallback (deterministic python-pptx):
```bash
python3 ppt-pro-studio/scripts/ppt_studio_generate.py examples/sample-brief.json --out deck.pptx
```

### Primary options

Renders the brief into high-fidelity vector SVG pages, then via the bundled
ppt-master `svg_to_pptx` into a native editable `.pptx`, then injects **random
page-flip transitions**. The ppt-master converter is **bundled offline** in
`vendor/ppt-master-scripts/` (no separate install needed).

```bash
python3 ppt-pro-studio/scripts/ppt_master_hifi.py examples/sample-brief.json \
    --out deck.pptx --keep-project ./hifi_project --style tech_dark
```

Options: `--out <file.pptx>`, `--keep-project <dir>` (keep intermediate SVG),
`--style {tech_dark,business_blue,creative_purple,academic_white,minimal_gray}`,
`--no-transition` (skip random animations), `--seed N` (reproducible effects),
`--transition-duration 0.5`.

---

## Prerequisites
- `python3` + `python-pptx` (pip install python-pptx) for rendering (both engines)
- `node >= 18` for the MCP server
- ppt-master converter is **bundled** in `vendor/ppt-master-scripts/` (offline, MIT) — no separate install
- No network, no API key, no account

## Verify install
```bash
node ppt-pro-studio/mcp-server/ppt-studio-mcp.js   # type: tools/list then Enter
# expect: generate_ppt, qa_check, list_styles
python3 ppt-pro-studio/scripts/ppt_master_hifi.py ppt-pro-studio/examples/sample-brief.json --out /tmp/test.pptx
python3 ppt-pro-studio/scripts/ppt_studio_generate.py ppt-pro-studio/examples/sample-brief.json --out /tmp/test2.pptx
```
