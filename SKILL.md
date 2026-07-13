---
name: ppt-pro-studio
description: >
  专业级 PPT 生产工作流技能（商用 / 可变现 / 零限制）。当用户要求制作演示文稿、PPT、
  幻灯片、商业汇报、路演材料、课程课件，或说"做个关于 X 的 PPT"时触发。工作流强制以
  **提示词增强**为首个步骤，将模糊需求转化为结构化制作简报，再经大纲→设计→渲染→质检→
  导出，产出可编辑、可商用的 .pptx。可独立运行，也可经 ppt-studio-mcp 被任意 MCP 大模型调用。
version: 1.0.0
license: MIT
metadata:
  openclaw:
    emoji: "\U0001F4D0"
    requires:
      bins: [python3, node]
    env: []
  engines:
    primary: pptx-generator (python-pptx)
    premium: ppt-master (true editable .pptx + animations)
    premium_hifi: ppt_master_hifi.py (self-contained wrapper -> ppt-master svg_to_pptx)
    universal: ppt-studio-mcp (any MCP LLM)
  prompt_enhancer: prompt-refiner-skill (MIT) / prompt-optimize (Alpha-Prompt)
visibility: public
---

# PPT Pro Studio — 专业 PPT 生产工作流

可商用、可变现、零限制的 PPT 生产线。从一句模糊的需求，到一份能直接拿去给客户演示、
能上传知识付费平台售卖的 .pptx。

## 设计原则（务必遵守）

1. **提示词增强是第一个、且不可跳过的步骤。** 用户给的往往是模糊需求
   （"做个 AI 的 PPT"）。必须先增强，再开工。未增强直接做 = 产出质量不达标。
2. **产出必须可编辑、可商用、无水印。** 一律生成原生 `.pptx`（文本框/形状/图表逐元素可改），
   不产出"整页截图式"PPT。
3. **零限制分发。** 本技能 MIT 许可；引用的子技能（prompt-refiner-skill MIT、
   ppt-master MIT、pptx-generator MIT-0、pptx-generator-mcp MIT）均为宽松许可，
   可自由集成、再分发、商用。**不引入 AGPL/双协议组件**（如 linshenkx/prompt-optimizer 为
   AGPL-3.0，禁止纳入商业分发）。
4. **可靠性优先。** 主渲染走 `ppt_studio_generate.py`（python-pptx），确定性、零网络、
   跨平台；ppt-master 作为"高保真 premium"可选路径。

## 生产管线（严格串行）

```
① 提示词增强 ──► ② 结构化简报 ──► ③ 大纲 ──► ④ 设计系统 ──► ⑤ 内容填充
      │                                                                        │
      └────────────────────────── ⑥ 渲染(.pptx) ──► ⑦ 质检门 ──► ⑧ 精修 ──► ⑨ 导出交付
```

### ① 提示词增强（MANDATORY · 第一步）

调用 **Prompt Refiner** 方法论（见 `references/prompt-refiner-PROMPT.md`，MIT），
将用户原始需求改写为 **outcome-first 的结构化制作简报**。要求补全以下维度：

- **主题 / Topic**：一句话核心命题。
- **受众 / Audience**：投资人？学员？客户？内部团队？决定措辞深度与例子。
- **目标 / Goal**：说服、教学、汇报、销售？决定叙事结构。
- **风格 / Style**：从 `{tech_dark, business_blue, creative_purple, academic_white, minimal_gray}` 选一。
- **页数 / Length**：建议 8–20 页（商业汇报 10–14 页最佳）。
- **章节 / Sections**：3–6 个一级模块，每个模块 1–3 页。
- **约束 / Constraints**：品牌色、禁用词、必须出现的概念、交付格式(.pptx/.pdf/网页)。
- **验收 / Acceptance**：什么叫"做好了"。

> 若已安装 `prompt-optimize`（Alpha-Prompt）技能，可叠加其"角色+结构化+护栏"优化。
> 增强结果是一份 **enhanced_brief.md**，后续步骤全部以它为准。

### ② 结构化简报 → ③ 大纲

基于 enhanced_brief，产出逐页大纲 `outline.json`，每页标注：
`{ type, title, subtitle?, items?/columns?/rows?/series? , num? }`。
版式类型（12 种，与渲染器一一对应）：
`cover, section, agenda, content, two_column, table, chart, timeline, quote, image, summary, contact`。

### ④ 设计系统

按所选 style 套用 `references/design-system.md` 的配色与排版。统一：
标题字体 28pt 主色、正文 15pt、卡片表面色、1px 分隔线、页脚+页码。
中文统一 `Microsoft YaHei`（非 Windows 自动回退默认字体）。

### ⑤ 内容填充

把大纲扩写为成稿文案。要点遵循"每页≤3 个核心点，每点一行可念"的商用铁律。
数据类页用 `table` / `chart`；流程类用 `timeline`；金句用 `quote`。

### ⑥ 渲染（生成 .pptx）

**主路径（推荐，确定性）：**
```bash
python3 scripts/ppt_studio_generate.py brief.json --out deliverable.pptx
```
`brief.json` 结构见 `examples/sample-brief.json`。

**Premium 路径（高保真真·可编辑 + 动画）：** 调用 `ppt-master` 技能
（已安装，`~/.workbuddy/skills/ppt-master`，MIT），走其 SVG→PPTX 管线，
适合对版式精度/动画有极致要求的客户交付。

**⑥-B Premium SVG→PPTX（可选按钮 · 自包含）** —— 一行命令把 brief 先渲染成
高保真矢量 SVG 页面，再经 ppt-master 的 `svg_to_pptx` 转为原生 `.pptx`（矢量形状/
文本逐元素可改）。无需手动调 ppt-master，本技能内置包装器 `scripts/ppt_master_hifi.py`：
```bash
# 依赖：ppt-master 技能已安装在 ~/.workbuddy/skills/ppt-master（MIT）
python3 scripts/ppt_master_hifi.py brief.json --out deliverable_hifi.pptx
# 可选：保留中间 SVG 工程目录以便二次精修
python3 scripts/ppt_master_hifi.py brief.json --out deliverable_hifi.pptx \
    --keep-project ./hifi_project --footer "PPT Pro Studio · 机密" --style tech_dark
```
返回 `{"ok": true, "engine": "ppt-master SVG->PPTX", "slides": N}`，产出原生可编辑
`.pptx`。与 ⑥ 主路径相比，⑥-B 走矢量 SVG 中间层，对复杂图表/自定义图形的保真度更高。

**MCP 路径（任意大模型调用）：** 任何支持 MCP 的 LLM 连接 `ppt-studio-mcp`
（见 `mcp-server/`），直接调用 `generate_ppt` 工具完成渲染，无需本技能文件。

### ⑦ 质检门（Quality Gate · 不可跳过）

对照 `references/qa-checklist.md` 逐条核对：
- [ ] 无空页、无占位符残留（如 `[图片缺失]` 必须补图或换版式）
- [ ] 文字无溢出/重叠，每页≤3 核心点
- [ ] 配色统一、品牌色正确
- [ ] 图表数据与文案一致
- [ ] 中文显示正常（非方块）
- [ ] 可编辑：PowerPoint/WPS 中能逐元素改
- [ ] 无水印、无外部服务依赖、可离线打开

MCP 用户可调用 `qa_check` 工具做程序化校验（页数、空页、占位符扫描）。

### ⑧ 精修 / ⑨ 导出交付

按反馈 loop 修正（改 brief.json 重渲染，不要手动改 .pptx 再丢失源）。
交付：`deliverable.pptx`（主）+ 可选 `deliverable.pdf` + 可选 `reveal.html`（直播/录屏）。

## 子技能与工具（均已安装 · 宽松许可）

| 角色 | 组件 | 许可 | 用途 |
|------|------|------|------|
| 提示词增强 | prompt-refiner-skill | MIT | ① 强制首步 |
| 提示词增强(备选) | prompt-optimize (Alpha-Prompt) | 本地技能 | 角色/结构化优化 |
| 主渲染引擎 | ppt_studio_generate.py (本技能) | MIT-0 | ⑥ 确定性渲染 |
| 主渲染引擎 | pptx-generator | MIT-0 | JSON→.pptx 备选 |
| Premium 渲染 | ppt-master | MIT | 高保真真·可编辑+动画 |
| Premium 渲染(包装) | ppt_master_hifi.py (本技能) | MIT | ⑥-B: brief→SVG→ppt-master→.pptx |
| 通用 MCP | ppt-studio-mcp (本技能) | MIT | 任意 MCP LLM 调用 |

## 触发词

"做PPT" "生成PPT" "制作演示文稿" "商业汇报" "路演材料" "课件" "create presentation"
"make a slide deck" "ppt for client" 或显式调用 `/ppt-pro-studio`。

## 安全 / 商业合规

- 全部组件 MIT / MIT-0，可商用、可再分发、可收费，**无 copyleft 义务**。
- 不收集用户数据，渲染全程本地，无外部网络调用（图片若需联网搜索由调用方决定）。
- 不产出受版权保护素材的仿冒品；用户需对其内容负责。
