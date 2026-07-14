---
name: ppt-pro-studio
description: >
  专业级 PPT 生产工作流技能（商用 / 可变现 / 零限制）。当用户要求制作演示文稿、PPT、
  幻灯片、商业汇报、路演材料、课程课件，或说"做个关于 X 的 PPT"时触发。工作流强制以
  **提示词增强**为首个步骤，将模糊需求转化为结构化制作简报，再经大纲→设计→渲染→质检→
  导出，产出可编辑、可商用的 .pptx。可独立运行，也可经 ppt-studio-mcp 被任意 MCP 大模型调用。
version: 1.3.0
license: MIT
metadata:
  openclaw:
    emoji: "\U0001F4D0"
    requires:
      bins: [python3, node]
    env: []
  engines:
    primary: ppt-master (hugohe3/ppt-master, 16.6k★, MIT) via ppt_master_hifi.py
    fallback: python-pptx (ppt_studio_generate.py, deterministic, zero extra deps)
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
4. **可靠性优先。** 主渲染走 `ppt_master_hifi.py`（ppt-master SVG→PPTX，
   hugohe3/ppt-master，16.6k★，MIT——星标最多的 PPTX 技能），矢量逐元素可编辑、
   自带随机翻页动画、零网络；`ppt_studio_generate.py`（python-pptx）作为确定性强回退，
   同样零网络、防溢出自动缩放。

## 生产管线（严格串行）

```
① 提示词增强 ──► ② 结构化简报 ──► ③ 大纲 ──► ④ 设计系统 ──► ⑤ 内容填充
      │                                                                        │
      └──── ⑥ 渲染（按 brief.delivery 路由）─────────────────────────────────┐
           ├─ editable（默认）→ 核心引擎 → 原生可编辑 .pptx                  │
           └─ showcase        → Marp HTML   → 视觉天花板 HTML PPT            ▼
                                                       ⑦ 质检门 ──► ⑧ 精修 ──► ⑨ 导出交付
```

### ① 提示词增强（MANDATORY · 第一步）

调用 **Prompt Refiner** 方法论（见 `references/prompt-refiner-PROMPT.md`，MIT），
将用户原始需求改写为 **outcome-first 的结构化制作简报**。要求补全以下维度：

- **主题 / Topic**：一句话核心命题。
- **受众 / Audience**：投资人？学员？客户？内部团队？决定措辞深度与例子。
- **目标 / Goal**：说服、教学、汇报、销售？决定叙事结构。
- **叙事结构 / Narrative**（P3-2 新增）：按 Goal 套骨架，brief 写 `narrative` 字段：
  - `persuade` 说服型（融资/销售/提案）：痛点→为什么是现在→方案→证明(数据/案例)→价值/ROI→行动号召。
  - `inform` 通知型（汇报/复盘/公告）：背景→关键进展(数据)→问题分析→结论→下一步。
  - `teach` 教学型（课程/培训）：目标→核心概念→原理→实战案例→随堂练习→小结。
  - `inspire` 激励型（路演/宣讲/动员）：愿景→共鸣→挑战/机遇→我们的行动→邀请同行。
  4 种骨架的逐页映射见 `references/prompt-refiner-PROMPT.md`「叙事结构」节。
- **风格 / Style**：从主题市场 `themes/`（`tech_dark, business_blue, creative_purple,
  academic_white, minimal_gray, fintech_green, sunset_orange, mono_ink,
  guochao_red, medical_blue, ecommerce_orange, gov_red`，共 12 套）
  选一，brief 用 `theme` 或 `style` 字段引用。自定义主题：往 `themes/` 丢一个
  JSON 即可（`python3 scripts/theme_market.py list` 浏览，`validate` 校验）。
- **页数 / Length**：建议 8–20 页（商业汇报 10–14 页最佳）。
- **章节 / Sections**：3–6 个一级模块，每个模块 1–3 页。
- **约束 / Constraints**：品牌色、禁用词、必须出现的概念、交付格式(.pptx/.pdf/网页)。
- **验收 / Acceptance**：什么叫"做好了"。
- **交付路径 / Delivery**（P3-2 新增）：brief 写 `delivery` 字段路由渲染引擎——
  `editable`（**默认**）→ 核心引擎产出**原生可编辑 .pptx**；`showcase` → Marp HTML
  路径（`scripts/ppt_marp.py`）产出**视觉天花板 HTML PPT**（+ 可选 PPTX/PDF 分发）。
  提示词增强阶段自动识别意图：命中「可编辑/二次修改/WPS 改/交付同事」→ `editable`；
  命中「震撼/视觉/演示/路演/吸引付费」且无编辑诉求 → `showcase`；兜底 `editable`。

> 若已安装 `prompt-optimize`（Alpha-Prompt）技能，可叠加其"角色+结构化+护栏"优化。
> 增强结果是一份 **enhanced_brief.md**，后续步骤全部以它为准。
> brief 关键字段：`topic, audience, goal, narrative, theme/style, length, sections,
> constraints, acceptance, delivery`。其中 `narrative` 与 `delivery` 为 P3-2 新增。

### ② 结构化简报 → ③ 大纲

基于 enhanced_brief，产出逐页大纲 `outline.json`，每页标注：
`{ type, title, subtitle?, items?/columns?/rows?/series? , num? }`。
版式类型（13 种，与渲染器一一对应）：
`cover, section, agenda, content, two_column, table, chart, timeline, quote,
image, media, summary, contact`。
其中 `media` 为**图文混排**（图片 + 文字左右排布），`image` 为整页大图。

### ④ 设计系统

按所选 style 套用 `references/design-system.md` 的配色与排版。统一：
标题字体 28pt 主色、正文 15pt、卡片表面色、1px 分隔线、页脚+页码。
中文统一 `Microsoft YaHei`（非 Windows 自动回退默认字体）。

### ④-b 主题市场 / 图文混排 / 演讲者备注（P2 能力）

**主题市场（Theme Market）。** 主题是一组可编辑的设计令牌
（`bg, surface, primary, secondary, text, muted, accent, line, font`），以
独立 JSON 存放在 `themes/`，渲染时按需加载并合并内置调色板。用户无需改引擎
代码即可扩展：拷贝任一 `*.json` 改色即新主题。CLI：
```bash
python3 scripts/theme_market.py list                # 浏览 8 套主题
python3 scripts/theme_market.py show fintech_green  # 查看令牌
python3 scripts/theme_market.py validate brief.json # 校验 brief 主题存在
python3 scripts/theme_market.py init                # 重置 themes/*.json
```
brief 用 `"theme": "fintech_green"`（或别名 `"style"`）切换；未知主题回退
`tech_dark`。品牌色仍写入母版 `theme1.xml`，PPT/WPS 面板一处改全局。

**图文混排（media）。** 版式 `media`：图片在一侧、文字块在另一侧
（`image_position: "left"|"right"`）。文字块支持 `heading` + `items`
（要点，兼容 `|` 详情）或自由 `text`。图片按原始比例 contain 适配并居中：
`python-pptx` 用 `add_picture` + PIL 计算比例；主路径把图片以 base64 data-URI
内嵌进 SVG（`preserveAspectRatio` 适配），零外部文件依赖。图片缺失时显示品牌
占位框。可选 `caption` 图注。示例：
```json
{"type":"media","title":"产品一览","image":"examples/assets/dashboard.png",
 "image_position":"left","heading":"为什么客户留下来",
 "items":["实时调用监控 | 异常自动告警","开箱即用看板 | 无需自建 BI"],
 "caption":"图：运营看板（演示数据）"}
```

**演讲者备注（notes）。** 任意页加 `"notes": "..."` 即写入演讲者备注栏：
`python-pptx` 走 `slide.notes_slide`；主路径把 `notes/page_NNN.md` 写入工程，
由 ppt-master 自动嵌入。备注不进入画面、不影响排版，纯给演讲者看。

### ⑤ 内容填充

把大纲扩写为成稿文案。要点遵循"每页≤3 个核心点，每点一行可念"的商用铁律。
数据类页用 `table` / `chart`；流程类用 `timeline`；金句用 `quote`。

### ⑥ 渲染（生成 .pptx）

**主路径（推荐 · 星标最多的 PPTX 技能 · 自带翻页动画）：**
```bash
python3 scripts/ppt_master_hifi.py brief.json --out deliverable.pptx
#   --no-transition       不注入随机翻页动画
#   --seed N              固定随机种子（可复现）
#   --transition-duration 0.5   单页动画时长(秒)
#   --keep-project ./proj       保留中间 SVG 工程目录便于二次精修
```
`brief.json` 结构见 `examples/sample-brief.json`。该路径把 brief 先渲染成高保真
矢量 SVG 页面，再经 ppt-master 的 `svg_to_pptx` 转为原生 `.pptx`（矢量形状/文本逐元素
可改），最后用 ppt-master 的过渡核心注入**随机翻页动画**。所有文本在 1280×720 画布内
自动换行并收缩字号，杜绝溢出。内置打包的 ppt-master 在 `vendor/ppt-master-scripts/`，
离线可用。

**回退路径（确定性 · 零额外依赖）：** 当主路径不可用（如 ppt-master 缺失且未解包）时，
自动回退到纯 python-pptx 渲染，同样零网络、同样做了防溢出（`TEXT_TO_FIT_SHAPE` 自动
缩放 + 动态行距 + 随机翻页动画）：
```bash
python3 scripts/ppt_studio_generate.py brief.json --out deliverable_fallback.pptx
```

**MCP 路径（任意大模型调用）：** 任何支持 MCP 的 LLM 连接 `ppt-studio-mcp`
（见 `mcp-server/`），直接调用 `generate_ppt` 工具完成渲染（内部同样主用 ppt-master、
回退 python-pptx；`delivery:"showcase"` 时走 Marp HTML 路径），无需本技能文件。

**统一入口 + 演示天花板（P3 新增）。** 用 `scripts/generate.py` 按 brief 的
`delivery` 字段自动路由，无需手选引擎：
```bash
python3 scripts/generate.py brief.json --out deck.pptx   # delivery=editable（默认）
python3 scripts/generate.py brief.json --out deck.html   # delivery=showcase
```
- `editable`（默认）→ 核心引擎产出**原生可编辑 .pptx**（客户可二次修改）。
- `showcase` → **Marp HTML 路径**（`scripts/ppt_marp.py`）产出**视觉天花板 HTML PPT**
  （主题 CSS 由 brief 主题 token 动态生成，一套源同时可出 PDF/PPTX 分发）：
  ```bash
  python3 scripts/ppt_marp.py brief.json --out deck.html [--pdf] [--pptx]
  ```
  > Marp 路径 HTML 永远可出；PDF/PPTX 需本机 Chromium（`--pdf`/`--pptx` 会自动跳过并提示）。
  > 适用：路演、品牌发布、吸睛展示——用视觉冲击力促单，而非交付可编辑生产件。

### ⑦ 质检门（Quality Gate · 不可跳过）

对照 `references/qa-checklist.md` 逐条核对：
- [ ] 无空页、无占位符残留（如 `[图片缺失]` 必须补图或换版式）
- [ ] 文字无溢出/重叠，每页≤3 核心点
- [ ] 配色统一、品牌色正确
- [ ] 图表数据与文案一致
- [ ] 中文显示正常（非方块）
- [ ] 可编辑：PowerPoint/WPS 中能逐元素改
- [ ] 翻页动画已注入（主路径默认开启）
- [ ] 无水印、无外部服务依赖、可离线打开

**QA 2.1 排版校验（推荐，程序化）**：渲染后跑
`python3 scripts/qa2.py deliverable.pptx [--json report.json]`，自动审计
边界越界、占位符残留、正文≥11pt 字号下限、翻页动画、矢量图标数量、母版品牌
主题一致性、演讲者备注页数、图片数量，并给出 0–100 评分。零 error 级问题即通过。

MCP 用户可调用 `qa_check` 工具做程序化校验（页数、空页、占位符扫描）。

### ⑧ 精修 / ⑨ 导出交付

按反馈 loop 修正（改 brief.json 重渲染，不要手动改 .pptx 再丢失源）。
交付：`deliverable.pptx`（主，ppt-master）+ 可选 `deliverable.pdf` + 可选 `deck.html`（直播/录屏）。

## UI 控制台（P3-10 · 本地向导 · v1.3.0 全面升级）

纯本地 `ui/console.html`（HTML/JS，零依赖，双击即开）：
- **模板市场可视化**：13 套行业模板卡片（含产品规格、数据报告、项目计划），点击即填充表单。
- **主题色卡实时预览**：12 套主题色板 + 自定义主题构建器，每套标注 WCAG 对比度等级（AAA/AA/不达标）。
- **自定义主题**：颜色选择器编辑 8 个色彩 token + 字体，实时预览 + 对比度检测，保存到 localStorage 或导出 JSON。
- **叙事结构下拉**：4 种骨架（persuade/inform/teach/inspire），切换自动重建页面大纲。
- **Delivery 路由切换**：editable（核心引擎 PPTX）↔ showcase（Marp HTML 视觉天花板）。
- **页面编辑器**：拖拽排序、点击展开编辑标题/类型/要点，支持 18 种页面布局类型。
- **布局选择器弹窗**：添加页面时弹出 18 种布局卡片（含列表页/详情页/表单页/仪表盘/对比页/数据统计），可视化选择。
- **步骤引导条**：选模板→填信息→选主题→调大纲→导出，5 步流程可视化引导。
- **表单校验**：必填项实时校验 + 错误提示，导出前全量校验。
- **键盘快捷键**：← → 翻页预览、Ctrl+D 下载、Ctrl+S 复制 JSON、Esc 关闭弹窗。
- **一键导出**：Download `brief.json` / Copy JSON / Copy 生成命令。

> 打开方式：浏览器直接打开 `ui/console.html`，或用 `python3 -m http.server` 起本地服务。

## 协作轻量版（P3-11 · 版本化 + 预览 + 导入）

离线 Skill 不做实时多人同屏编辑（交给云端协作层），但提供三个可操作的协作能力：

1. **Git 版本化**：`scripts/collab.py init --dir ./my-deck` 脚手架项目（`briefs/` + `output/` +
   `.gitattributes` + README），每版 brief + 产物入 git，可追溯/可分支/可 diff。
   详见 `COLLABORATION.md`。
2. **局域网预览**：`scripts/collab.py serve --dir output --port 8848` 一键启动 HTTP 服务，
   自动检测 LAN IP，手机/平板同网段浏览器直接看 HTML PPT。
3. **导入乐享/腾讯文档**：`scripts/collab.py export --brief brief.json --out deck.md`
   将 brief 导出为 Markdown（每页一个 `##` 标题 + 要点列表），粘贴到乐享/腾讯文档/飞书/Notion
   即可做多人评论与协同编辑。如已配置乐享 MCP，AI 可自动完成导入。

## 回退引擎防溢出预计算（P3-6）

`ppt_studio_generate.py` 的防溢出从「事后缩 gap + TEXT_TO_FIT_SHAPE」升级为「事前预计算」：
- `_fit_bullets()` 在渲染前计算所有 bullet items 的总高度，主动缩小字号（直至 FONT_FLOOR 11pt），
  仍溢出则截断末尾 items 并加省略号——不再依赖 WPS/PowerPoint 的 autofit 行为。
- 表格单元格 `_cell_font()` 新增 `col_width_in` 参数，按列宽预计算字号，
  替代不可靠的 `TEXT_TO_FIT_SHAPE`。
- 回归验证：14 页 QA 2.1 仍 100/100，零越界/零截断/零误报。

## 新增页面布局类型（P3-12 · v1.3.0）

在原有 12 种页面类型（cover/section/content/two_column/media/chart/table/timeline/quote/agenda/summary/contact）基础上新增 6 种布局：

| 类型 | 标签 | 适用场景 | 渲染要点 |
|------|------|----------|----------|
| `list_page` | 列表页 | 功能清单、检查项、步骤说明 | 卡片式行项 + 图标 + 左侧 accent 边框 + 右侧序号 |
| `detail_page` | 详情页 | 产品规格、人物介绍、项目档案 | 2 列键值对网格 + surface 卡片背景 |
| `form_page` | 表单页 | 流程说明、填写引导、问卷调查 | 右对齐标签 + 下划线值域 |
| `dashboard` | 仪表盘 | KPI 概览、数据监控、运营看板 | 多列卡片 + 顶部彩色边框 + 大号数值 |
| `comparison` | 对比页 | 方案选择、竞品分析、优劣对比 | 多列对比 + 中间列高亮(primary 填充) |
| `stats` | 数据统计 | 核心指标、增长数据、业绩展示 | 大号数字横排 + 每项独立配色 |

- 全部 6 种新类型已在 `ppt_studio_generate.py` 注册到 RENDERERS，可直接渲染。
- `template_market.py` 新增 3 套使用新布局的模板：`product_spec`、`data_report`、`project_plan`。
- `theme_market.py` 新增 `mode`（dark/light）字段 + WCAG 对比度检测函数（`contrast_ratio()`、`check_contrast()`）。
- 修复兼容性：`build()` 方法同时读取 `brief["slides"]` 和 `brief["pages"]`。

## 子技能与工具（均已安装 · 宽松许可）

| 角色 | 组件 | 许可 | 用途 |
|------|------|------|------|
| 提示词增强 | prompt-refiner-skill | MIT | ① 强制首步 |
| 提示词增强(备选) | prompt-optimize (Alpha-Prompt) | 本地技能 | 角色/结构化优化 |
| **主渲染引擎** | **ppt_master_hifi.py → ppt-master** | MIT | ⑥ 主路径：SVG→PPTX+动画（16.6k★ 最高星标） |
| 回退渲染引擎 | ppt_studio_generate.py (本技能) | MIT-0 | ⑥ 确定性回退：python-pptx + 预计算防溢出 |
| 演示天花板 | ppt_marp.py + Marp CLI | MIT | ⑥ showcase 路径：Markdown→HTML/PDF/PPTX |
| 统一路由 | generate.py (本技能) | MIT-0 | ⑥ 按 delivery 字段自动选引擎 |
| 模板市场 | template_market.py (本技能) | MIT-0 | 10 套行业模板，CLI + MCP |
| 主题市场 | theme_market.py (本技能) | MIT-0 | 12 套行业调色板 |
| UI 控制台 | ui/console.html (本技能) | MIT-0 | 本地向导：填表→预览→导出 brief |
| 协作工具 | collab.py (本技能) | MIT-0 | git 版本化 + LAN 预览 + 导出 Markdown |
| QA 校验 | qa2.py (本技能) | MIT-0 | ⑦ QA 2.1 排版审计（PPTX + HTML） |
| 通用 MCP | ppt-studio-mcp (本技能) | MIT | 任意 MCP LLM 调用 |

## 触发词

"做PPT" "生成PPT" "制作演示文稿" "商业汇报" "路演材料" "课件" "create presentation"
"make a slide deck" "ppt for client" 或显式调用 `/ppt-pro-studio`。

## 安全 / 商业合规

- 全部组件 MIT / MIT-0，可商用、可再分发、可收费，**无 copyleft 义务**。
- 不收集用户数据，渲染全程本地，无外部网络调用（图片若需联网搜索由调用方决定）。
- 不产出受版权保护素材的仿冒品；用户需对其内容负责。
